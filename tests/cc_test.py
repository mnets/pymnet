import unittest
from operator import itemgetter

import sys
sys.path.append("../../")
from pymnet import net,cc,models
#from .. import net


class TestNet(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_unweighted_flat_triangle(self):
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

    def test_weighted_flat_simple(self):
        pass #TODO

    def test_unweighted_mplex_triangle(self):
        def add_clique(net,level):
            net[1,2,level]=1
            net[1,3,level]=1
            net[2,3,level]=1

        n=net.CoupledMultiplexNetwork([('categorical',1.0)])
        add_clique(n,1)
        add_clique(n,2)
        add_clique(n,3)
        add_clique(n,4)

        an=net.MultisliceNetwork(dimensions=1)
        an[1,2]=4
        an[1,3]=4
        an[2,3]=4

        #barrett
        self.assertEqual(cc.cc_barrett(n,1,an),128./96.)
        self.assertEqual(cc.cc_barrett(n,1,an),cc.cc_barrett_explicit(n,1))

        #cc seq
        self.assertEqual(cc.cc_sequence(n,1),([1,1,1,1],[1,1,1,1]))

        print cc.cc_cycle_vector_bf(n,1,1)
        print cc.cc_cycle_vector_adj(n,1,1)

    def test_unweighted_mplex_simple(self):
        n=net.CoupledMultiplexNetwork([('categorical',1.0)])

        n[1,2,1]=1
        n[1,3,1]=1
        n[2,3,1]=1

        n[1,2,2]=1
        n[1,3,2]=1
        n[1,4,2]=1
        n[3,4,2]=1

        n[1,2,3]=1
        n[1,3,3]=1
        n[1,4,3]=1
        n[2,4,3]=1

        an=net.MultisliceNetwork(dimensions=1)
        an[1,2]=3
        an[1,3]=3
        an[1,4]=2
        an[2,3]=1
        an[3,4]=1
        an[2,4]=1

        self.assertEqual(cc.cc_barrett(n,1,an),cc.cc_barrett_explicit(n,1))

    def test_unweighted_consistency_er(self):
        net=models.er(10,[0.4,0.6,0.5,0.3])
        self.assertEqual(cc.cc_cycle_vector_bf(net,1,1),cc.cc_cycle_vector_adj(net,1,1))

def test_net():
    suite = unittest.TestSuite()    
    suite.addTest(TestNet("test_unweighted_flat_triangle"))
    suite.addTest(TestNet("test_unweighted_flat_simple"))
    suite.addTest(TestNet("test_unweighted_mplex_triangle"))
    suite.addTest(TestNet("test_unweighted_mplex_simple"))
    suite.addTest(TestNet("test_unweighted_consistency_er"))

    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_net()

