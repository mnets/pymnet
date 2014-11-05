import unittest
from operator import itemgetter

import sys
sys.path.append("../../")
from pymnet import net,transforms



class TestTransforms(unittest.TestCase):
    
    def setUp(self):
        n=net.MultiplexNetwork([('categorical',1.0)])

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

        self.mplex_simple=n

        n=net.MultiplexNetwork([('categorical',1.0)],fullyInterconnected=False)

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

        self.mplex_nonaligned_simple=n

    def test_aggregate_unweighted_mplex_simple(self):
        an=transforms.aggregate(self.mplex_simple,1)
        self.assertEqual(an[1,2],3)
        self.assertEqual(an[1,3],3)
        self.assertEqual(an[1,4],2)
        self.assertEqual(an[2,3],1)
        self.assertEqual(an[3,4],1)
        self.assertEqual(an[2,4],1)

    def test_aggregate_2dim_mplex(self):
        n=net.MultiplexNetwork([('categorical',1.0),('categorical',1.0)])
        n[1,2,'a','x']=3
        n[2,3,'a','x']=1
        n[1,2,'b','x']=1
        n[1,3,'b','x']=1
        n[1,2,'c','x']=1
        n[1,3,'c','x']=1
        n[2,3,'c','x']=1

        n[1,2,'b','y']=1
        n[2,3,'b','y']=1
        n[1,2,'c','y']=1
        n[1,3,'c','y']=1
        n[1,2,'a','y']=1
        n[1,3,'a','y']=1
        n[2,3,'a','y']=1

        an1=transforms.aggregate(n,1)
        self.assertEqual(an1[1,2,'x'],5)
        self.assertEqual(an1[1,3,'x'],2)
        self.assertEqual(an1[2,3,'x'],2)
        self.assertEqual(an1[1,2,'y'],3)
        self.assertEqual(an1[1,3,'y'],2)
        self.assertEqual(an1[2,3,'y'],2)

        an2=transforms.aggregate(n,2)
        self.assertEqual(an2[1,2,'a'],4)
        self.assertEqual(an2[1,3,'a'],1)
        self.assertEqual(an2[2,3,'a'],2)
        self.assertEqual(an2[1,2,'b'],2)
        self.assertEqual(an2[1,3,'b'],1)
        self.assertEqual(an2[2,3,'b'],1)
        self.assertEqual(an2[1,2,'c'],2)
        self.assertEqual(an2[1,3,'c'],2)
        self.assertEqual(an2[2,3,'c'],1)

        an3=transforms.aggregate(n,(1,2))
        self.assertEqual(an3[1,2],8)
        self.assertEqual(an3[1,3],4)
        self.assertEqual(an3[2,3],4)
        self.assertEqual(an3,transforms.aggregate(an1,1))
        self.assertEqual(an3,transforms.aggregate(an2,1))


    def test_subnet_mplex_simple(self):
        copynet=transforms.subnet(self.mplex_simple,[1,2,3,4],[1,2,3])
        self.assertEqual(copynet,self.mplex_simple)
        import copy
        copynet2=copy.deepcopy(self.mplex_simple)
        self.assertEqual(copynet2,self.mplex_simple)

    def test_aggregate_2dim_mlayer_nonglobal_nodes(self):
        def test_net(n):
            n[1,2,'a','x']=3
            n.add_layer('b',1)
            n.add_layer('y',2)
            n.add_node(3,layer=('a','x'))
            n.add_node(4,layer=('c','z'))
            an1=transforms.aggregate(n,1)
            self.assertEqual(set(an1),set([1,2,3,4]))
            self.assertEqual(set(an1.iter_node_layers()),set([(1,'x'),(2,'x'),(3,'x'),(4,'z')]))
            an2=transforms.aggregate(n,2)
            self.assertEqual(set(an2),set([1,2,3,4]))
            self.assertEqual(set(an2.iter_node_layers()),set([(1,'a'),(2,'a'),(3,'a'),(4,'c')]))
        mln=net.MultilayerNetwork(aspects=2,fullyInterconnected=False)
        test_net(mln)
        mpn=net.MultiplexNetwork([('categorical',1.0),('categorical',1.0)],fullyInterconnected=False)
        test_net(mpn)

    def test_aggregate_1dim_mlayer_nonglobal_nodes(self):
        def test_net(n):
            n[1,2,'a']=1
            n.add_layer('b')
            n.add_node(3,layer=('a'))
            n.add_node(4,layer=('c'))
            an=transforms.aggregate(n,1)
            self.assertEqual(set(an),set([1,2,3,4]))
            self.assertEqual(an[1,2],1)
            self.assertEqual(an.aspects,0)
        mln=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        test_net(mln)
        mpn=net.MultiplexNetwork([('categorical',1.0)],fullyInterconnected=False)
        test_net(mpn)
   
    def test_aggregate_2dim_mlayer_interlayeredges(self):
        n=net.MultilayerNetwork(aspects=2,fullyInterconnected=False)
        n[1,'a','x'][2,'b','y']=3
        n[1,'c','x'][2,'d','y']=1
        n[1,'a','x'][2,'b','x']=1
        an1=transforms.aggregate(n,1)
        self.assertEqual(set(an1.edges),set([(1,2,'x','y',4),(1,2,'x','x',1)]))
        an2=transforms.aggregate(n,2)
        self.assertEqual(set(an2.edges),set([(1,2,'a','b',4),(1,2,'c','d',1)]))
        an3=transforms.aggregate(n,(1,2))
        self.assertEqual(set(an3.edges),set([(1,2,5)]))
        self.assertEqual(an3,transforms.aggregate(an1,1))
        self.assertEqual(an3,transforms.aggregate(an2,1))


    def test_normalize_mplex_simple(self):
        n=net.MultiplexNetwork([('categorical',1.0)])

        n[0,1,0]=1
        n[0,2,0]=1
        n[1,2,0]=1

        n[0,1,1]=1
        n[0,2,1]=1
        n[0,3,1]=1
        n[2,3,1]=1

        n[0,1,2]=1
        n[0,2,2]=1
        n[0,3,2]=1
        n[1,3,2]=1

        self.assertEqual(transforms.normalize(self.mplex_simple),n)

        n=net.MultiplexNetwork([('categorical',1.0)],fullyInterconnected=False)

        n[0,1,0]=1
        n[0,2,0]=1
        n[1,2,0]=1

        n[0,1,1]=1
        n[0,2,1]=1
        n[0,3,1]=1
        n[2,3,1]=1

        n[0,1,2]=1
        n[0,2,2]=1
        n[0,3,2]=1
        n[1,3,2]=1

        try:
            self.assertEqual(transforms.normalize(self.mplex_nonaligned_simple),n)
        except Exception,e:
            self.assertEqual(str(e),"Not implemented.")

def test_transforms():
    suite = unittest.TestSuite()    
    suite.addTest(TestTransforms("test_aggregate_unweighted_mplex_simple"))
    suite.addTest(TestTransforms("test_aggregate_2dim_mplex"))
    suite.addTest(TestTransforms("test_aggregate_2dim_mlayer_nonglobal_nodes"))
    suite.addTest(TestTransforms("test_aggregate_1dim_mlayer_nonglobal_nodes"))
    suite.addTest(TestTransforms("test_aggregate_2dim_mlayer_interlayeredges"))
    suite.addTest(TestTransforms("test_subnet_mplex_simple"))
    suite.addTest(TestTransforms("test_normalize_mplex_simple"))
    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_transforms()

