import unittest
from operator import itemgetter
import sys


from pymnet import net,transforms,diagnostics



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

        #The 2-aspect example network for the review article
        n=net.MultilayerNetwork(aspects=2,fullyInterconnected=False)
        n[1,2,'A','A','X','X']=1
        n[2,3,'A','A','Y','Y']=1
        n[1,3,'B','B','X','X']=1
        n[1,4,'B','B','X','X']=1
        n[3,4,'B','B','X','X']=1
        n[1,1,'A','B','X','X']=1
        n[1,4,'A','B','X','X']=1
        n[1,1,'B','B','X','Y']=1
        n[3,3,'A','A','X','Y']=1
        n[3,4,'A','B','X','Y']=1
        self.mlayer_example_2d=n

        n=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        n[1,2,'A','A']=1
        n[2,3,'A','A']=1
        n[1,3,'B','B']=1
        n[1,4,'B','B']=1
        n[3,4,'B','B']=1
        n[1,1,'A','B']=1
        n[1,4,'A','B']=1
        n[3,4,'A','B']=1
        self.mlayer_example_1d=n

        n=net.MultilayerNetwork(aspects=0,fullyInterconnected=True)
        n[1,2]=1
        n[2,3]=1
        n[1,3]=1
        n[1,4]=2
        n[3,4]=2
        self.mlayer_example_monoplex=n

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

    def test_subnet_mlayer_example(self):
        #monoplex
        copynet=transforms.subnet(self.mlayer_example_monoplex,[1,2,3,4])
        self.assertEqual(copynet,self.mlayer_example_monoplex)
        copynet=transforms.subnet(self.mlayer_example_monoplex,None)
        self.assertEqual(copynet,self.mlayer_example_monoplex)
        import copy
        copynet2=copy.deepcopy(self.mlayer_example_monoplex)
        self.assertEqual(copynet2,self.mlayer_example_monoplex)

        n=net.MultilayerNetwork(aspects=0,fullyInterconnected=True)
        n[2,3]=1
        n[3,4]=2
        self.assertEqual(n,transforms.subnet(self.mlayer_example_monoplex,[2,3,4]))


        #1-aspect
        copynet=transforms.subnet(self.mlayer_example_1d,[1,2,3,4],['A','B'])
        self.assertEqual(copynet,self.mlayer_example_1d)
        copynet=transforms.subnet(self.mlayer_example_1d,None,['A','B'])
        self.assertEqual(copynet,self.mlayer_example_1d)
        copynet=transforms.subnet(self.mlayer_example_1d,None,None)
        self.assertEqual(copynet,self.mlayer_example_1d)
        copynet=transforms.subnet(self.mlayer_example_1d,[1,2,3,4],None)
        self.assertEqual(copynet,self.mlayer_example_1d)
        import copy
        copynet2=copy.deepcopy(self.mlayer_example_1d)
        self.assertEqual(copynet2,self.mlayer_example_1d)

        n=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        n[2,3,'A','A']=1
        self.assertEqual(n,transforms.subnet(self.mlayer_example_1d,[2,3,4],['A']))

        #2-aspect
        copynet=transforms.subnet(self.mlayer_example_2d,[1,2,3,4],['A','B'],['X','Y'])
        self.assertEqual(copynet,self.mlayer_example_2d)
        import copy
        copynet2=copy.deepcopy(self.mlayer_example_2d)
        self.assertEqual(copynet2,self.mlayer_example_2d)

        n=net.MultilayerNetwork(aspects=2,fullyInterconnected=False)
        n[3,4,'B','B','X','X']=1
        n.add_node(2,layer=('A','X'))
        n.add_node(3,layer=('A','X'))
        self.assertEqual(n,transforms.subnet(self.mlayer_example_2d,[2,3,4],None,['X','dummy']))



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

        nmap={1:0,2:1,3:2,4:3}
        lmap={1:0,2:1,3:2}
        self.assertEqual(transforms.normalize(self.mplex_simple),n)
        self.assertEqual(transforms.normalize(self.mplex_simple,nodesToIndices=True),(n,nmap))
        self.assertEqual(transforms.normalize(self.mplex_simple,layersToIndices=True),(n,lmap))
        self.assertEqual(transforms.normalize(self.mplex_simple,nodesToIndices=True,layersToIndices=True),(n,nmap,lmap))

        nmapr={0:1,1:2,2:3,3:4}
        lmapr={0:1,1:2,2:3}
        self.assertEqual(transforms.normalize(self.mplex_simple,nodesToIndices=False),(n,nmapr))
        self.assertEqual(transforms.normalize(self.mplex_simple,layersToIndices=False),(n,lmapr))
        self.assertEqual(transforms.normalize(self.mplex_simple,nodesToIndices=False,layersToIndices=False),(n,nmapr,lmapr))



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

        self.assertEqual(transforms.normalize(self.mplex_nonaligned_simple),n)


    def test_randomize_nodes_by_layer(self):
        n=transforms.randomize_nodes_by_layer(self.mplex_nonaligned_simple)
        self.assertNotEqual(n,self.mplex_nonaligned_simple)
        self.assertEqual(diagnostics.multiplex_degs(n),diagnostics.multiplex_degs(self.mplex_nonaligned_simple))


    def test_subnet_mplex_to_mlayer(self):
        mplex=net.MultiplexNetwork([('categorical',1.0)],fullyInterconnected=False)

        mplex[0,1,0]=1
        mplex[0,2,1]=1

        mlayer=transforms.subnet(mplex,[0,1,2],[0,1],newNet=net.MultilayerNetwork(aspects=1,fullyInterconnected=False))

        self.assertEqual(set(mlayer.edges),set([(0, 0, 0, 1, 1.0), (0, 1, 0, 0, 1), (0, 2, 1, 1, 1)]))
        self.assertTrue(isinstance(mlayer,net.MultilayerNetwork))
        
        self.assertRaises(TypeError,lambda :transforms.subnet(mlayer,[0,1,2],[0,1],newNet=net.MultiplexNetwork([('categorical',1.0)])))        



        mplex=net.MultiplexNetwork([('categorical',1.0)],fullyInterconnected=True)

        mplex[0,1,0]=1
        mplex[0,2,1]=1

        mlayer=transforms.subnet(mplex,[0,1,2],[0,1],newNet=net.MultilayerNetwork(aspects=1))

        self.assertEqual(set(mlayer.edges),set([(0, 0, 0, 1, 1.0), (0, 1, 0, 0, 1), (0, 2, 1, 1, 1), (1, 1, 0, 1, 1.0), (2, 2, 0, 1, 1.0)]))
        self.assertTrue(isinstance(mlayer,net.MultilayerNetwork))

        
    def test_subnet_different_interconnectivities(self):
        fully_interc = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        fully_interc[1,'X'][1,'Y'] = 1
        fully_interc[1,'X'][2,'X'] = 1
        other_fully_interc = transforms.subnet(fully_interc,fully_interc.get_layers(aspect=0),fully_interc.get_layers(aspect=1),newNet=net.MultilayerNetwork(aspects=1,fullyInterconnected=True))
        self.assertEqual(set(other_fully_interc.iter_node_layers()),set([(1, 'X'), (1, 'Y'), (2, 'X'), (2, 'Y')]))        
        
        fully_interc = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        fully_interc[1,'X'][1,'Y'] = 1
        fully_interc[1,'X'][2,'X'] = 1
        non_fully_interc = transforms.subnet(fully_interc,fully_interc.get_layers(aspect=0),fully_interc.get_layers(aspect=1),newNet=net.MultilayerNetwork(aspects=1,fullyInterconnected=False))
        self.assertEqual(set(non_fully_interc.iter_node_layers()),set([(1, 'X'), (1, 'Y'), (2, 'X'), (2, 'Y')]))
        
        non_fully_interc = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        non_fully_interc[1,'X'][1,'Y'] = 1
        non_fully_interc[1,'X'][2,'X'] = 1
        non_fully_interc.add_node(2,layer='Y')
        other_non_fully_interc = transforms.subnet(non_fully_interc,non_fully_interc.get_layers(aspect=0),non_fully_interc.get_layers(aspect=1),newNet=net.MultilayerNetwork(aspects=1,fullyInterconnected=False))
        self.assertEqual(set(other_non_fully_interc.iter_node_layers()),set([(1, 'X'), (1, 'Y'), (2, 'X'), (2, 'Y')]))
        
        non_fully_interc = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        non_fully_interc[1,'X'][1,'Y'] = 1
        non_fully_interc[1,'X'][2,'X'] = 1
        self.assertRaises(TypeError,lambda :transforms.subnet(non_fully_interc,non_fully_interc.get_layers(aspect=0),non_fully_interc.get_layers(aspect=1),newNet=net.MultilayerNetwork(aspects=1,fullyInterconnected=True)))


def test_transforms():
    suite = unittest.TestSuite()    
    suite.addTest(TestTransforms("test_aggregate_unweighted_mplex_simple"))
    suite.addTest(TestTransforms("test_aggregate_2dim_mplex"))
    suite.addTest(TestTransforms("test_aggregate_2dim_mlayer_nonglobal_nodes"))
    suite.addTest(TestTransforms("test_aggregate_1dim_mlayer_nonglobal_nodes"))
    suite.addTest(TestTransforms("test_aggregate_2dim_mlayer_interlayeredges"))
    suite.addTest(TestTransforms("test_subnet_mlayer_example"))
    suite.addTest(TestTransforms("test_subnet_mplex_simple"))
    suite.addTest(TestTransforms("test_subnet_mplex_to_mlayer"))
    suite.addTest(TestTransforms("test_subnet_different_interconnectivities"))
    suite.addTest(TestTransforms("test_normalize_mplex_simple"))
    suite.addTest(TestTransforms("test_randomize_nodes_by_layer"))
    
    return unittest.TextTestRunner().run(suite).wasSuccessful() 

if __name__ == '__main__':
    sys.exit(not test_transforms())

