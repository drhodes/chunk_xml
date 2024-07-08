import copy
import hashlib
from lxml import etree
from token_count import TokenCount

def show(el):            
    return etree.tostring(el, encoding="utf-8").decode("utf-8")

class XmlDoc():
    def __init__(self, xml_src):
        pass

class ChunkMgr():
    ''' Decompose XML into smaller chunks that can be reassembled '''
    
    def __init__(self, tree, token_limit, model_name):
        self.tree = tree
        self.token_limit = token_limit
        self.model_name = model_name
        self.chunk = Chunk(self.tree, token_limit, model_name)
        # self.chunks = self.chunk.decompose()

def hash_el(el):
    s = etree.tostring(el, encoding="utf-8").decode("utf-8")
    return hashlib.md5(s.encode()).hexdigest()[:16]

class Chunk():
    '''
    '''    
    def __init__(self, element, token_limit, model_name):
        self.element = element 
        self.token_limit = token_limit
        self.model_name = model_name
        self.init_hash = self.hash()
        
    def element_num_tokens(self, el):        
        tc = TokenCount(model_name=self.model_name) # 
        el_str = etree.tostring(el).decode("utf-8")
        num_tokens = tc.num_tokens_from_string(el_str)
        return num_tokens

    def too_big(self, el):
        return self.element_num_tokens(el) > self.token_limit

    def recompose(self):
        pass

    def build_ref(self, hashid):
        ref = etree.Element("chunk-ref")
        ref.attrib["id"] = hashid
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
        
        bust it into a sequence of 3 decomposed elements. 
        · <split>
            <a>
              <chunk-ref id="123"/>
              <chunk-ref id="456"/>
            <a/>
          </split>        
        · <chunk id="123"> <b> ... </b> <c> ... </c> </chunk>
        · <chunk id="456"> <d> ... </d> <e> ... </e> </chunk>
        
        The first element of a folded chunk is the parent.
        not all the elements will fit into the folded chunk.
        so:
        '''
        cs = el.getchildren()
        n = len(cs)//2
        els_left, els_right = cs[:n], cs[n:]

        left = etree.Element("chunk")
        left.extend(els_left)
        left_id = hash_el(left)
        left.attrib["id"] = left_id
        
        right = etree.Element("chunk")
        right.extend(els_right)
        right_id = hash_el(right)
        right.attrib["id"] = right_id

        split = etree.Element("split")
        inner = copy.deepcopy(el)
        for c in inner.getchildren():
            inner.remove(c)
            
        inner.append(self.build_ref(left_id))
        inner.append(self.build_ref(right_id))
        split.append(inner)
        return [split, left, right]
    
    def split_one(self, el):
        '''
        situation, suppose el is heavily nested with only
        one child element and looks something like:
        
                <a>
                    <b> 
                        <c>
                            <d> ... </d>
                        </c>
                    </b>
                </a>
        
        the previous tactic is ineffective since el has only
        one child element. No problem, just dig down another
        element and continue on.
        
        · <split> <a> <b> <chunk-ref id="123"/> </b> </a> </split>
        
        · <chunk id="123"> <c> <d> ... </d> </c> </chunk>

        '''
        assert len(el.getchildren()) == 1
        
        clone = copy.deepcopy(el)        
        cs = clone.getchildren()[0] # recall, el only has one child element
        rest_els = cs.getchildren()

        # remove the clone's grandchildren
        for e in cs.getchildren():
            cs.remove(e);

        # create the rest chunk
        rest = etree.Element("chunk")
        rest.extend(rest_els)
        rest_id = hash_el(rest)
        rest.attrib["id"] = rest_id
        
        split = etree.Element("split-one")
        cs.append(self.build_ref(rest_id))
        split.append(clone)
        
        return [split, rest]
        
    def join(self, split, left, right):
        pass
    
    def decompose(self, el):
        # todo, consider getting rid of the split elements
        # also, may need to track the root element.
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

    
    def __str__(self):
        return etree.tostring(self.element, encoding="utf-8").decode("utf-8")

    @staticmethod
    def from_str(xml_string, token_limit, model_name):
        el = etree.fromstring(xml_string)
        return Chunk(el, token_limit, model_name)
    
    def hash(self):
        return hashlib.md5(str(self).encode()).hexdigest()[:16]
