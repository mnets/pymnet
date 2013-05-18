import unittest
from operator import itemgetter

import sys
sys.path.append("../../")
from pymnet import net,cc
#from .. import net


class TestNet(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_unweighted_flat_single_triangle(self):
        n=net.MultisliceNetwork(dimensions=1)
        n[1,2]=1
        n[2,3]=1
        n[3,1]=1

        self.assertEqual(cc.cc(n,1),1.0)
        self.assertEqual(cc.cc_zhang(n,1),1.0)
        self.assertEqual(cc.cc_onnela(n,1),1.0)
        self.assertEqual(cc.cc_barrat(n,1),1.0)


    def test_unweighted_flat_simple(self):
        n=net.MultisliceNetwork(dimensions=1)
        n[1,2]=1
        n[2,3]=1
        n[3,1]=1
        n[1,4]=1

        self.assertEqual(cc.cc(n,1),1./3.)
        self.assertEqual(cc.cc_zhang(n,1),1./3.)
        self.assertEqual(cc.cc_onnela(n,1),1./3.)
        self.assertEqual(cc.cc_barrat(n,1),1./3.)


def test_net():
    suite = unittest.TestSuite()    
    suite.addTest(TestNet("test_unweighted_flat_single_triangle"))
    suite.addTest(TestNet("test_unweighted_flat_simple"))

    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_net()

