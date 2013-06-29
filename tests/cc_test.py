import unittest
from operator import itemgetter

import sys
sys.path.append("../../")
from pymnet import net,cc,models,transforms
import itertools
import random
import pymnet.net

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

        #cc moreno
        print "m ",
        print cc.gcc_moreno(n)
        print "m2 ",
        print cc.gcc_moreno2(n)

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

    def test_unweighted_consistency(self,net):
        anet=transforms.aggregate(net,1)
        onet=transforms.overlay_network(net)
        wmax=max(map(lambda x:x[2],anet.edges))
        owmax=max(map(lambda x:x[2],onet.edges))
        b=len(net.slices[1])

        if cc.cc_cycle_vector_bf(net,1,1)!=cc.cc_cycle_vector_adj(net,1,1):
            print list(anet.edges)
            print list(net.edges)
        self.assertEqual(cc.cc_cycle_vector_bf(net,1,1),cc.cc_cycle_vector_adj(net,1,1))

        #----
        t=0
        node=1
        for i,j in itertools.combinations(anet[node],2):
            t+=anet[node][i]*anet[node][j]*anet[i][j]
        d=0
        for i,j in itertools.combinations(anet[node],2):
            d+=anet[node][i]*anet[node][j]*len(net.slices[1])
        #print 2*t,2*d

        lt=0
        ld=0
        for l in net.slices[1]:
            aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc.cc_cycle_vector_bf(net,1,l)
            lt+= aaa+aacac+acaac+acaca+acacac
            ld+= afa+afcac+acfac+acfca+acfcac            
        #print lt,ld
        self.assertEqual(2*t,lt)
        self.assertEqual(2*d,ld)

        cc.gcc_alternating_walks_vector_adj(net)

        self.assertAlmostEqual(cc.gcc_alternating_walks_seplayers(net,w1=0.3,w2=0.3,w3=0.3),cc.gcc_alternating_walks_seplayers_adj(net,w1=0.3,w2=0.3,w3=0.3))

        for supernode in net.slices[0]:
            if abs(cc.sncc_alternating_walks(net,supernode,a=0.5,b=0.5)-wmax/float(b)*cc.cc_zhang(anet,supernode))>10**-6:
                print wmax,b,cc.sncc_alternating_walks(net,supernode,a=0.5,b=0.5),cc.cc_zhang(anet,supernode)
                print supernode
                print list(anet.edges)
                print list(net.edges)
            self.assertAlmostEqual(cc.sncc_alternating_walks(net,supernode,a=0.5,b=0.5),wmax/float(b)*cc.cc_zhang(anet,supernode))

        #global cc
        tga=0
        tgaw=0
        tgmoreno=0
        for node in net:
            for i,j in itertools.combinations(anet[node],2):
                tga+=2*anet[node][i]*anet[node][j]*anet[i][j]
            for l in net.slices[1]:
                aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc.cc_cycle_vector_bf(net,node,l)
                tgaw+=aaa+aacac+acaac+acaca+acacac
                tgmoreno+=aaa+2*aacac+2*acaac+acaca+2*acacac
        print "gcc_t",tga,tgaw,tgmoreno
        """
        print "gcc",cc.gcc_contraction_m(net),cc.gcc_contraction_m_ct(net),cc.gcc_super_graph(net),cc.gcc_contraction_o2(net),owmax*cc.gcc_zhang(onet)/float(b),cc.gcc_contraction_o(net)
        """

    def test_unweighted_consistency_mslice(self,net):
        anet=transforms.aggregate(net,1)
        onet=transforms.overlay_network(net)
        wmax=max(map(lambda x:x[2],anet.edges))
        owmax=max(map(lambda x:x[2],onet.edges))
        b=len(net.slices[1])

        self.assertAlmostEqual(cc.gcc_contraction_m(net),cc.gcc_contraction_m_ct(net))
        self.assertAlmostEqual(cc.gcc_contraction_m_ct(net),cc.gcc_contraction_m_full(net))
        #self.assertAlmostEqual(cc.gcc_contraction_m_full(net),cc.gcc_super_graph(net))

        self.assertAlmostEqual(cc.gcc_contraction_o2(net),owmax*cc.gcc_zhang(onet)/float(b))
        self.assertAlmostEqual(cc.gcc_contraction_o2(net),cc.gcc_contraction_o_full(net))

        print "gcc_0,02,Oz,b,wmax:",cc.gcc_contraction_o(net),cc.gcc_contraction_o2(net),cc.gcc_zhang(onet),b,owmax

        #print "gcc",cc.gcc_contraction_m(net),cc.gcc_contraction_m_ct(net),cc.gcc_contraction_m_full(net),cc.gcc_super_graph(net),cc.gcc_contraction_o2(net),owmax*cc.gcc_zhang(onet)/float(b),cc.gcc_contraction_o(net)


    def test_unweighted_consistency_mslice_er(self):
        net=models.er_multislice(10,5,0.5,randomWeights=True)
        self.test_unweighted_consistency_mslice(net)

        net=models.er_multislice(10,5,0.1,randomWeights=True)
        self.test_unweighted_consistency_mslice(net)

    def test_normalization_full_mslice(self):
        net=models.full_multislice(5,5)
        self.assertEqual(cc.gcc_contraction_m(net),1.0)
        self.assertEqual(cc.gcc_contraction_m_ct(net),1.0)
        self.assertEqual(cc.gcc_contraction_m_full(net),1.0)
        self.assertEqual(cc.gcc_super_graph(net),1.0)

        self.assertEqual(cc.gcc_contraction_o2(net),1.0)
        self.assertEqual(cc.gcc_contraction_o_full(net),1.0)

        onet=transforms.overlay_network(net)
        owmax=max(map(lambda x:x[2],onet.edges))
        b=len(net.slices[1])
        self.assertEqual(owmax*cc.gcc_zhang(onet)/float(b),1.0)
        self.assertEqual(owmax,b)

        self.assertNotEqual(cc.gcc_contraction_o(net),1.0)


    def test_unweighted_consistency_er(self):
        net=models.er(10,[0.9,0.1])
        net=models.er(10,[0.1,0.3])
        net=models.er(10,[0.4,0.6,0.5,0.3])
        for i in range(10):        
            net=models.er(10,[random.random(),random.random(),random.random()])
            self.test_unweighted_consistency(net)

        net=pymnet.net.CoupledMultiplexNetwork([('categorical',1.0)])
        net[1, 9, 1, 1]=1 
        net[2, 9, 1, 1]=1  
        net[2, 4, 1, 1]=1  
        net[5, 8, 0, 0]=1  
        self.test_unweighted_consistency(net)

        net=pymnet.net.CoupledMultiplexNetwork([('categorical',1.0)])
        #net.add_node(1,0)
        net.add_node(1,1)
        net.add_node(2,1)
        net.add_node(3,1)
        net.add_node(4,1)
        net[1,2,1,1]=1
        net[1,3,1,1]=1
        net[2,3,1,1]=1
        self.test_unweighted_consistency(net)

        #net=models.full_multislice(10,5)
        #self.test_unweighted_consistency(net)

def test_net():
    suite = unittest.TestSuite()    
    suite.addTest(TestNet("test_unweighted_flat_triangle"))
    suite.addTest(TestNet("test_unweighted_flat_simple"))
    suite.addTest(TestNet("test_unweighted_mplex_triangle"))
    suite.addTest(TestNet("test_unweighted_mplex_simple"))
    suite.addTest(TestNet("test_unweighted_consistency_er"))
    suite.addTest(TestNet("test_unweighted_consistency_mslice_er"))
    suite.addTest(TestNet("test_normalization_full_mslice"))
    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_net()

