import pytest
from lxml import etree
from token_count import TokenCount
from random_tree import random_el
from chunk_xml.chunk import ChunkMgr
from chunk_xml.chunk import Chunk


def show(el):            
    return etree.tostring(el, encoding="utf-8").decode("utf-8")

def pp(el):            
    return etree.tostring(el, pretty_print=True, encoding="utf-8").decode("utf-8")


class TestChunkMgr():
    def hash_cmp(self, xml_string):
        '''
        see if a string can be roundtripped turned into a chunk
        then hashed to h1, then from chunk back to string, then back
        to chunk and hashed again. Do we get the same hash? 
        '''
        s1 = xml_string
        c1 = Chunk.from_str(s1, 100, "gpt-4o")
        s2 = str(c1)
        c2 = Chunk.from_str(s2, 100, "gpt-4o")
        assert c1.hash() == c2.hash()
        

    def test_hash_cmp_1(self): self.hash_cmp("<a> ... </a>")
    def test_hash_cmp_2(self): self.hash_cmp("<a> <b> ... </b> </a>")
    def test_hash_cmp_3(self): self.hash_cmp("<a> ... <b> ... </b> ... </a>")
    def test_hash_cmp_4(self): self.hash_cmp("<a> <b> asdf </b> asdf </a>")

    # generate random xml and ensure that hashes match.
    def test_hash_cmd_rand(self):        
        max_depth = 5
        for i in range(30):
            s = etree.tostring(random_el(i%max_depth))
            self.hash_cmp(s)


def test_decompose_1():
    xml = '''
    <e>
      <d1> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d1>
      <d2> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d2>
      <d3> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d3>
      <d4> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d4>
    </e>
    '''
    el = etree.fromstring(xml)
    cm = ChunkMgr(100, "gpt-4o")
    chunks = cm.decompose(el)

def test_decompose_2():
    xml = '''
    <e>
      <d1> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d1>
      <d2> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d2>
      <d3> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d3>
      <d4> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d4>
    </e>
    '''
    el = etree.fromstring(xml)
    cm = ChunkMgr(100, "gpt-4o")    
    xs = cm.decompose(el)
    for x in xs:
        print(str(xs))
    
def test_decompose_rand():
    cm = ChunkMgr(500, "gpt-4o")
    for depth in range(4, 10):
        el = random_el(depth)
        chunks = cm.decompose(el)

def test_decompose_file():
    xml_src = open("tests/cases/m49435-index.cnxml").read()
    el = etree.fromstring(xml_src)
    cm = ChunkMgr(500, "gpt-4o")
    xs = cm.decompose(el)


def test_decompose_recursion_error():
    xml = '''
    <e>
      <d1> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d1>
      <d2> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d2>
      <d3> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d3>
      <d4> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d4>
    </e>
    '''
    with pytest.raises(RecursionError) as e:
        el = etree.fromstring(xml)
        cm = ChunkMgr(100, "gpt-4o")
        
        # resize the token_limit to cause problems!
        cm.token_limit = 10
        cm.decompose(el)


def test_contains_chunk_ref():
    xml = '''
    <e>
      <d1> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d1>
      <d2> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d2>
      <d3> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d3>
      <d4> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d4>
    </e>
    '''
    el1 = etree.fromstring(xml)
    cm = ChunkMgr(100, "gpt-4o")
    chunks = cm.decompose(el1)
    root = chunks[0]
    root.contains_chunk_ref()

def test_recompose():
    xml = '''
    <e>
      <d1> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d1>
      <d2> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d2>
      <d3> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d3>
      <d4> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d4>
    </e>
    '''
    el1 = etree.fromstring(xml)
    cm = ChunkMgr(100, "gpt-4o")
    chunks = cm.decompose(el1)
    el2 = cm.recompose(chunks)

    s1 = show(etree.fromstring(xml))
    s2 = show(el2)
    assert s1 == s2

    
def test_recompose_rand():
    max_depth = 8
    for i in range(100):
        xml = etree.tostring(random_el(i%max_depth))
        el1 = etree.fromstring(xml)
        cm = ChunkMgr(100, "gpt-4o")
        chunks = cm.decompose(el1)
        el2 = cm.recompose(chunks)
        
        s1 = show(etree.fromstring(xml))
        s2 = show(el2)
        assert s1 == s2

    
def recompose_file(fname):
    xml = open(fname).read()
    parser = etree.XMLParser(remove_comments=True)
    el = etree.fromstring(xml, parser=parser)
    cm = ChunkMgr(500, "gpt-4o")
    chunks = cm.decompose(el)
    el2 = cm.recompose(chunks)
        
    s1 = pp(etree.fromstring(xml, parser=parser))
    s2 = pp(el2)
    assert s1 == s2


def test_recompose_file_m49435():
    recompose_file("tests/cases/m49435-index.cnxml")
    
def test_recompose_file_m49368():
    recompose_file("tests/cases/m49368-index.cnxml")
