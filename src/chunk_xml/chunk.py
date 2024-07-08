import copy
import hashlib
from lxml import etree
from token_count import TokenCount

def show(el):            
    return etree.tostring(el, encoding="utf-8").decode("utf-8")

def hash_el(el):
    s = etree.tostring(el, encoding="utf-8").decode("utf-8")
    return hashlib.md5(s.encode()).hexdigest()[:16]

CHUNK_REF_TAG = "__chunk_ref"
CHUNK_VAL_TAG = "__chunk_val"

# todo: setup logging
def warn(x): print(x)


class XmlDoc():
    def __init__(self, xml_src):
        pass


class Chunk():
    '''
    '''    
    def __init__(self, element, token_limit, model_name):
        self.element = element 
        self.token_limit = token_limit
        self.model_name = model_name
        self.init_hash = self.hash()

    @staticmethod
    def from_str(xml_string, token_limit, model_name):
        parser = etree.XMLParser(remove_comments=True)
        el = etree.fromstring(xml_string, parser=parser)
        return Chunk(el, token_limit, model_name)

    def hash(self):
        return hashlib.md5(str(self).encode()).hexdigest()[:16]

    def __str__(self):
        return etree.tostring(self.element, encoding="utf-8").decode("utf-8")
    
    def is_chunk_ref(self):
        return self.element.tag == CHUNK_REF_TAG
        
    def is_chunk_val(self):
        return self.element.tag == CHUNK_VAL_TAG
    
    def chunk_id(self):
        if self.is_chunk_ref() or self.is_chunk_val():
            return self.element.attrib["id"]
        else:
            raise Exception(f"Trying to get the chunk id of an element that is not a chunk.")

    def next_chunk_ref(self):
        return self.element.find('.//' + CHUNK_REF_TAG)
        
    def contains_chunk_ref(self):
        return False if self.next_chunk_ref() is None else True

  
    
class ChunkMgr():
    ''' Decompose XML into smaller chunks that can be recompose '''
   
    def __init__(self, token_limit, model_name):
        if token_limit < 100:
            warn("token limit too small, increasing")
            self.token_limit = 100
        else:
            self.token_limit = token_limit
        self.model_name = model_name
        self.__cur_id = 0


    def gen_next_id(self):
        self.__cur_id += 1
        return str(self.__cur_id)
        
    def element_num_tokens(self, el):        
        tc = TokenCount(model_name=self.model_name) # 
        el_str = etree.tostring(el).decode("utf-8")
        num_tokens = tc.num_tokens_from_string(el_str)
        return num_tokens

    def too_big(self, el):
        return self.element_num_tokens(el) > self.token_limit

    def recompose(self):
        pass

    def build_ref(self, chunk_id):
        ref = etree.Element(CHUNK_REF_TAG)
        ref.attrib["id"] = chunk_id
        return ref
    
    def split_many(self, el):
        '''
        suppose el has more than one child element
        <a>
          <b> ... </b>
          <c> ... </c>
          <d> ... </d>
          <e> ... </e>
        </a>                  
        
        bust it into a sequence of 3 smaller elements. 
        · <a>
            <__chunk_ref id="123"/>
            <__chunk_ref id="456"/>
          <a/>
          
        · <chunk id="123"> <b> ... </b> <c> ... </c> </chunk>
        · <chunk id="456"> <d> ... </d> <e> ... </e> </chunk>
        
        The first element of a folded chunk is the parent.
        not all the elements will fit into the folded chunk.
        so:
        '''
        cs = el.getchildren()
        n = len(cs)//2
        els_left, els_right = cs[:n], cs[n:]

        left = etree.Element(CHUNK_VAL_TAG)
        left.extend(els_left)
        left_id = self.gen_next_id()
        left.attrib["id"] = left_id
        
        right = etree.Element(CHUNK_VAL_TAG)
        right.extend(els_right)
        right_id = self.gen_next_id()
        right.attrib["id"] = right_id

        inner = copy.deepcopy(el)
        for c in inner.getchildren():
            inner.remove(c)
            
        inner.append(self.build_ref(left_id))
        inner.append(self.build_ref(right_id))
        return [inner, left, right]
    
    def split_one(self, el):
        '''
        Suppose el is heavily nested with only
        one child element and looks something like:
        
                <a>
                    <b> 
                        <c>
                            <d> ... </d>
                        </c>
                    </b>
                </a>
        
        the previous tactic is ineffective since el has only one child
        element, that is, divide and conquer won't work on one
        element. No problem! Instead, "unnest", by digging down another
        element and continue on.
        
        · <a> <b> <__chunk_ref id="123"/> </b> </a>         
        · <__chunk_val id="123"> <c> <d> ... </d> </c> </__chunk_val>
        '''
        assert len(el.getchildren()) == 1
        
        clone = copy.deepcopy(el)        
        cs = clone.getchildren()[0] # recall, el only has one child element
        rest_els = cs.getchildren()

        # remove the clone's grandchildren
        for e in cs.getchildren():
            cs.remove(e);

        # create the rest chunk
        rest = etree.Element(CHUNK_VAL_TAG)
        rest.extend(rest_els)
        rest_id = self.gen_next_id()
        rest.attrib["id"] = rest_id
        
        # this mutates the clone.
        cs.append(self.build_ref(rest_id))
        return [clone, rest]
       
    def decomp(self, el):
        '''
        Return a list of chunks that can be reassembled into the
        original tree.  currently limitation, does not handle text or
        tail that exceed token_limit
        '''
        if self.too_big(el):
            cs = el.getchildren()
            if len(cs) == 0:                
                # todo: handle case of no children and large text section 
                raise Exception("Library limitation encountered, can't split large text, tail.")
            
            if len(cs) > 1:
                # if there is more than one child element 
                s, l, r = self.split_many(el)
                return self.decompose(s) + self.decompose(l) + self.decompose(r)
            
            else:
                # if there is only one child element
                split, rest = self.split_one(el)
                return self.decompose(split) + self.decompose(rest)
        else:
            return [Chunk(el, self.token_limit, self.model_name)]


    def decompose(self, el):
        try:
            return self.decomp(el)
        except RecursionError as e:
            print("! --------------------------------------------------------------")
            print("! HINT: ")
            print("! ")
            print("! This is probably because your token limit is set too low.")
            print("! Try increasing the token_limit give to ChunkMgr constructor")
            raise e

    def build_chunk_table(self, chunks):        
        chunks_vals = {}
        for c in chunks:
            if c.is_chunk_val():
                chunks_vals[c.chunk_id()] = c
        return chunks_vals
        
    def recompose(self, chunks):
        '''
        rebuild root by replacing chunk references with chunk
        elements
        '''
        root, rest = chunks[0], chunks[1:]

        # build lookup table from: chunk_id => chunk_value
        chunk_table = self.build_chunk_table(rest)

        def replace_ref(ref_el, chunk):
            '''
            replace the occurance of ref_el with the children of chunk.
            this mutates the tree in place.
            '''
            par = ref_el.getparent()
            idx = par.index(ref_el)
            par.remove(ref_el)
            for el in reversed(chunk.element.getchildren()):
                par.insert(idx, el)
        
        while root.contains_chunk_ref():
            ref = root.next_chunk_ref()
            
            # el looks like <chunk-ref id="123"/>, it needs to be
            # replaced with the innards of the following chunk
            cid = ref.attrib["id"]
            
            matching_chunk = chunk_table.get(cid, None)
            if matching_chunk == None:
                raise Exception(f"LIBRARY BUG: chunk with id {cid} not found in chunk table")
            
            # replace chunk ref with chunk value child elements.
            replace_ref(ref, matching_chunk)

        return root.element
            
            
            
        
            
            
        
        
    
    
