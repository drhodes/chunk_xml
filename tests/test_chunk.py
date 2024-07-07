import pytest
from lxml import etree
from token_count import TokenCount
from random_tree import random_el
from chunk_xml.chunk import ChunkMgr
from chunk_xml.chunk import Chunk

    
class TestChunkMgr():
    @staticmethod
    def raw_data1():
        # ensure the test data
        return '''
        <document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML">
        <title>Solving Systems with Inverses</title>
        <metadata xmlns:md="http://cnx.rice.edu/mdml">
        <md:content-id>m49435</md:content-id>
        <md:title>Solving Systems with Inverses</md:title>
        <md:abstract><para id="para-00001">In this section, you will:</para><list id="list-00001">
        <item>Find the inverse of a matrix.</item>
        <item>Solve a system of linear equations using an inverse matrix.</item>
        </list></md:abstract>
        <md:uuid>634d2387-7429-480f-a04e-867c2f9699fb</md:uuid>
        </metadata>
        </document>
        '''
    
    def test_asdf(self):
        root = etree.fromstring(TestChunkMgr.raw_data1())
        cm = ChunkMgr(root, 100, "gpt-4o")
        
class TestChunk():
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
    def test_hash_cmp_5(self): self.hash_cmp(TestChunkMgr.raw_data1())

    # generate random xml and ensure that hashes match.
    def test_hash_cmd_rand(self):        
        max_depth = 7
        for i in range(100):
            s = etree.tostring(random_el(i%max_depth))
            self.hash_cmp(s)


def show(el):            
    return etree.tostring(el, encoding="utf-8").decode("utf-8")

def test_decompose_1():
    xml = '''
    <e>
      <d1> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d1>
      <d2> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d2>
      <d3> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d3>
      <d4> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d4>
    </e>
    '''
    c = Chunk.from_str(xml, 10, "gpt-4o")
    s, l, r = c.split_many(c.element)



def test_decompose_2():
    xml = '''
    <e>
      <d1> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d1>
      <d2> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d2>
      <d3> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d3>
      <d4> <c><b><a></a></b><b><a></a></b></c> <c><b><a></a></b><b><a></a></b></c> </d4>
    </e>
    '''
    
    c = Chunk.from_str(xml, 100, "gpt-4o")
    xs = c.decompose(c.element)
    
