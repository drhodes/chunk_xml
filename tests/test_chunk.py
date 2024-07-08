import pytest
from lxml import etree
from token_count import TokenCount
from random_tree import random_el
from chunk_xml.chunk import ChunkMgr
from chunk_xml.chunk import Chunk


def show(el):            
    return etree.tostring(el, encoding="utf-8").decode("utf-8")


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
