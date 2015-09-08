import unittest
import sys
sys.path.append("../../")

from pymnet import net,nxwrap
import networkx

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

        self.assertEqual(networkx.connected_components(nnx),[[1, 2, 3], [4, 5]])

    def test_monoplex_basics_writing_pymnet(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=1
        nnx=nxwrap.MonoplexGraphNetworkxView(n)
        n[2,3]=3
        n[4,5]=4
        
        self.test_monoplex_basics(nnx)

    def test_monoplex_basics_writing_nx(self):
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

    def test_autowrapping(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=1
        n[2,3]=1
        n[4,5]=1        

        self.assertEqual(nxwrap.connected_components(n),[[1, 2, 3], [4, 5]])

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
        self.assertNotEqual(networkx.Graph,nxwrap.MonoplexGraphNetworkxNew)


def test_nxwrap():
    suite = unittest.TestSuite()    
    suite.addTest(TestNxwrap("test_monoplex_basics_writing_pymnet"))
    suite.addTest(TestNxwrap("test_monoplex_basics_writing_nx"))
    suite.addTest(TestNxwrap("test_monoplex_load_karate")) 
    suite.addTest(TestNxwrap("test_autowrapping"))
    suite.addTest(TestNxwrap("test_mst"))
    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_nxwrap()

