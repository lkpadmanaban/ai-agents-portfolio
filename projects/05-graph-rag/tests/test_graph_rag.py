import sys, os, unittest
from pathlib import Path

# Ensure the src package is on PYTHONPATH
sys.path.append(os.path.abspath('projects/graph-rag/src'))
from graph_rag import GraphRAG

class TestGraphRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create a temporary edge CSV
        cls.edge_file = Path('temp_edges.csv')
        cls.edge_file.write_text('A,B\nB,C\nC,D')
        cls.rag = GraphRAG(str(cls.edge_file))

    @classmethod
    def tearDownClass(cls):
        cls.edge_file.unlink()

    def test_load_edges(self):
        self.assertIn('A', self.rag.graph)
        self.assertIn('B', self.rag.graph)
        self.assertIn('C', self.rag.graph)
        self.assertIn('D', self.rag.graph)
        self.assertIn('B', self.rag.graph['A'])
        self.assertIn('A', self.rag.graph['B'])

    def test_subgraph_depth_1(self):
        nodes = self.rag.subgraph('B', depth=1)
        self.assertSetEqual(set(nodes), {'A', 'B', 'C'})

    def test_generate_answer(self):
        ans = self.rag.generate_answer('What is connected to B?', 'B')
        self.assertIn('A', ans)
        self.assertIn('C', ans)

if __name__ == '__main__':
    unittest.main()
