import unittest
import sys

from pymnet import net,nxwrap
import networkx
import itertools

class TestNxwrap(unittest.TestCase):    
    def setUp(self):
        pass

    def test_monoplex_basics(self,nnx):
        self.assertEqual(nnx[1][2]['weight'],1)
        self.assertEqual(nnx[2][3]['weight'],3)
        self.assertEqual(nnx[4][5]['weight'],4)

        self.assertEqual(nnx[2][1]['weight'],1)
        self.assertEqual(nnx[3][2]['weight'],3)
        self.assertEqual(nnx[5][4]['weight'],4)

        self.assertEqual(set(map(frozenset,networkx.connected_components(nnx))),set([frozenset([1, 2, 3]), frozenset([4, 5])]))

    def test_monoplex_basics_writing_pymnet(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=1
        nnx=nxwrap.MonoplexGraphNetworkxView(n)
        n[2,3]=3
        n[4,5]=4
        
        self.test_monoplex_basics(nnx)

    def test_monoplex_basics_writing_nx_nxversion1(self):
        n=net.MultilayerNetwork(aspects=0)
        nnx=nxwrap.MonoplexGraphNetworkxView(n)
        nnx.add_node(1)
        nnx.add_nodes_from([2,3,4,5])
        nnx.add_edge(1,2)
        nnx[2][3]=3
        nnx.add_edge(4,5)
        nnx[4][5]=1
        nnx[4][5]=4
        
        self.test_monoplex_basics(nnx)

    def test_monoplex_basics_writing_nx(self):
        n=net.MultilayerNetwork(aspects=0)
        nnx=nxwrap.MonoplexGraphNetworkxView(n)
        nnx.add_node(1)
        nnx.add_nodes_from([2,3,4,5])
        nnx.add_edge(1,2)
        nnx.add_edge(2,3,weight=3)
        nnx.add_edge(4,5)
        nnx.add_edge(4,5,weight=1)
        nnx.add_edge(4,5,weight=4)
        
        self.test_monoplex_basics(nnx)

    def test_autowrapping(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=1
        n[2,3]=1
        n[4,5]=1        

        self.assertEqual(set(map(frozenset,nxwrap.connected_components(n))),set([frozenset([1, 2, 3]), frozenset([4, 5])]))

    def test_mst(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=1
        n[2,3]=1
        n[1,3]=10

        mst=nxwrap.minimum_spanning_tree(n)

        self.assertEqual(mst[1,2],1)
        self.assertEqual(mst[2,3],1)
        self.assertEqual(mst[1,3],mst.noEdge)


    def test_monoplex_load_karate(self):
        knet=nxwrap.karate_club_graph()
        self.assertEqual(knet.__class__,net.MultilayerNetwork)
        self.assertEqual(set(range(34)),set(knet))
        self.assertEqual(len(knet.edges),78)
        self.assertEqual(knet[0,1],1)
        #self.assertNotEqual(networkx.Graph,nxwrap.MonoplexGraphNetworkxNew)


    def test_monoplex_tuples_nxversion1(self):
        n=net.MultilayerNetwork(aspects=0)
        nnx=nxwrap.MonoplexGraphNetworkxView(n)
        nnx.add_node((1,'a'))
        nnx.add_nodes_from([(2,'a'),(3,'a'),(4,'a'),(5,'a')])
        nnx.add_edge((1,'a'),(2,'a'))
        nnx[(2,'a')][(3,'a')]=3
        nnx.add_edge((4,'a'),(5,'a'))
        nnx[(4,'a')][(5,'a')]=1
        nnx[(4,'a')][(5,'a')]=4
        
        self.assertEqual(nnx[(1,'a')][(2,'a')]['weight'],1)
        self.assertEqual(nnx[(2,'a')][(3,'a')]['weight'],3)
        self.assertEqual(nnx[(4,'a')][(5,'a')]['weight'],4)

        self.assertEqual(nnx[(2,'a')][(1,'a')]['weight'],1)
        self.assertEqual(nnx[(3,'a')][(2,'a')]['weight'],3)
        self.assertEqual(nnx[(5,'a')][(4,'a')]['weight'],4)

        self.assertEqual(set(map(frozenset,networkx.connected_components(nnx))),set([frozenset([(1,'a'), (2,'a'), (3,'a')]), frozenset([(4,'a'), (5,'a')])]))

    def test_monoplex_tuples(self):
        n=net.MultilayerNetwork(aspects=0)
        nnx=nxwrap.MonoplexGraphNetworkxView(n)
        nnx.add_node((1,'a'))
        nnx.add_nodes_from([(2,'a'),(3,'a'),(4,'a'),(5,'a')])
        nnx.add_edge((1,'a'),(2,'a'))
        nnx.add_edge((2,'a'),(3,'a'),weight=3)
        nnx.add_edge((4,'a'),(5,'a'))
        nnx.add_edge((4,'a'),(5,'a'),weight=1)
        nnx.add_edge((4,'a'),(5,'a'),weight=4)
        
        self.assertEqual(nnx[(1,'a')][(2,'a')]['weight'],1)
        self.assertEqual(nnx[(2,'a')][(3,'a')]['weight'],3)
        self.assertEqual(nnx[(4,'a')][(5,'a')]['weight'],4)

        self.assertEqual(nnx[(2,'a')][(1,'a')]['weight'],1)
        self.assertEqual(nnx[(3,'a')][(2,'a')]['weight'],3)
        self.assertEqual(nnx[(5,'a')][(4,'a')]['weight'],4)

        self.assertEqual(set(map(frozenset,networkx.connected_components(nnx))),set([frozenset([(1,'a'), (2,'a'), (3,'a')]), frozenset([(4,'a'), (5,'a')])]))

    def test_grid_graph(self):
        gg=nxwrap.grid_graph([2,3])
        if int(networkx.__version__.split(".")[0])>=2: #The grid is produced in reversed order in networkx 2.
            self.assertEqual(set(gg),set(itertools.product(range(3),range(2))))
        else:
            self.assertEqual(set(gg),set(itertools.product(range(2),range(3))))

def test_nxwrap():
    suite = unittest.TestSuite()    
    suite.addTest(TestNxwrap("test_monoplex_basics_writing_pymnet"))
    suite.addTest(TestNxwrap("test_monoplex_basics_writing_nx"))
    suite.addTest(TestNxwrap("test_monoplex_load_karate")) 
    suite.addTest(TestNxwrap("test_monoplex_tuples")) 
    suite.addTest(TestNxwrap("test_grid_graph")) 
    suite.addTest(TestNxwrap("test_autowrapping"))
    suite.addTest(TestNxwrap("test_mst"))
    
    return unittest.TextTestRunner().run(suite).wasSuccessful()  

if __name__ == '__main__':
    sys.exit(not test_nxwrap())

