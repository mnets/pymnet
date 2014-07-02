import unittest
import sys
sys.path.append("../../")

from pymnet import net,nxwrap
import networkx

class TestNxwrap(unittest.TestCase):    
    def setUp(self):
        pass

    def test_monoplex_basics(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=2
        nnx=nxwrap.MonoplexGraphNetworkxView(n)
        n[2,3]=3
        n[4,5]=4

        self.assertEqual(nnx[1][2]['weight'],2)
        self.assertEqual(nnx[2][3]['weight'],3)
        self.assertEqual(nnx[4][5]['weight'],4)

        self.assertEqual(nnx[2][1]['weight'],2)
        self.assertEqual(nnx[3][2]['weight'],3)
        self.assertEqual(nnx[5][4]['weight'],4)

        self.assertEqual(networkx.connected_components(nnx),[[1, 2, 3], [4, 5]])

    def test_autowrapping(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=1
        n[2,3]=1
        n[4,5]=1        

        self.assertEqual(nxwrap.connected_components(n),[[1, 2, 3], [4, 5]])


def test_nxwrap():
    suite = unittest.TestSuite()    
    suite.addTest(TestNxwrap("test_monoplex_basics"))
    suite.addTest(TestNxwrap("test_autowrapping"))
    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_nxwrap()

