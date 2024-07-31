This is a small library for chunking XML into smaller valid XML
chunks. It essentially flattens the tree structure.

Current limitation: Large text and tail sections are not split.

The idea is that you have some $f$ that you'd like to apply to each
chunk, as shown below.  This is helpful in some LLM workflows where
the context size is limited.

![image](https://github.com/drhodes/chunk_xml/assets/84929/3a611c01-7656-4cd8-8fb6-1a88e439cc74)
