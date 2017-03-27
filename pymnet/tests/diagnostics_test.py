import unittest
import sys

from pymnet import net,diagnostics,models,nx


class TestDiagnostics(unittest.TestCase):    
    def setUp(self):
        pass

    def create_chain(self,net):
        net[1,2]=1
        net[2,3]=1
        net[3,4]=1

    def create_chain_mplex(self,net):
        net.add_layer(1)
        net.add_layer(2)
        net.add_layer(3)
        self.create_chain(net.A[1])
        self.create_chain(net.A[3])
        

    def test_monoplex_density_degs(self,net,dnet):
        self.create_chain(net)
        self.create_chain(dnet)

        self.assertEqual(diagnostics.density(net),3/float((4*3)/2))
        #self.assertEqual(diagnostics.density(dnet),3/float(4*3))

        self.assertEqual(diagnostics.degs(net),{1:2,2:2})
        self.assertEqual(diagnostics.degs(net,degstype="nodes"),{1:1,4:1,2:2,3:2})
        #self.assertEqual(diagnostics.degs(dnet),{1:2,2:2})

    def test_monoplex_density_degs_mnet(self):
        n=net.MultilayerNetwork(aspects=0,directed=False)        
        dn=net.MultilayerNetwork(aspects=0,directed=True)        
        self.test_monoplex_density_degs(n,dn)


    def test_multiplex_density_degs(self,net):
        self.create_chain_mplex(net)

        self.assertEqual(diagnostics.multiplex_density(net),{1:0.5,2:0,3:0.5})
        if net.fullyInterconnected:
            self.assertEqual(diagnostics.multiplex_degs(net),{1:{1:2,2:2},2:{0:4},3:{1:2,2:2}})
        else:
            self.assertEqual(diagnostics.multiplex_degs(net),{1:{1:2,2:2},2:{},3:{1:2,2:2}})

    def test_multiplex_density_degs_mnet(self):
        n=net.MultiplexNetwork(couplings='none',directed=False)        
        self.test_multiplex_density_degs(n)
        n=net.MultiplexNetwork(couplings='categorical',directed=False)        
        self.test_multiplex_density_degs(n)
        n=net.MultiplexNetwork(couplings='none',directed=False,fullyInterconnected=False)        
        self.test_multiplex_density_degs(n)

    def test_multilayer_degs_multilayernet(self):
        n=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        n[1,2,3,4]=1
        n[1,2,3,3]=1
        self.assertEqual(diagnostics.degs(n,degstype="distribution"),{1:2,2:1})
        self.assertEqual(diagnostics.degs(n,degstype="nodes"),{(1,3):2,(2,3):1,(2,4):1})


    def test_multilayer_degs_mplexnet(self):
        n=net.MultiplexNetwork(couplings="none",fullyInterconnected=True)
        self.create_chain_mplex(n)
        self.assertEqual(diagnostics.degs(n,degstype="nodes"),{(1,1):1,(2,1):2,(3,1):2,(4,1):1,(1,3):1,(2,3):2,(3,3):2,(4,3):1,(1,2):0,(2,2):0,(3,2):0,(4,2):0})

        n=net.MultiplexNetwork(couplings="none",fullyInterconnected=False)
        self.create_chain_mplex(n)
        self.assertEqual(diagnostics.degs(n,degstype="nodes"),{(1,1):1,(2,1):2,(3,1):2,(4,1):1,(1,3):1,(2,3):2,(3,3):2,(4,3):1})

        n=net.MultiplexNetwork(couplings="categorical",fullyInterconnected=True)
        self.create_chain_mplex(n)
        self.assertEqual(diagnostics.degs(n,degstype="nodes"),{(1,1):3,(2,1):4,(3,1):4,(4,1):3,(1,3):3,(2,3):4,(3,3):4,(4,3):3,(1,2):2,(2,2):2,(3,2):2,(4,2):2})

        n=net.MultiplexNetwork(couplings="categorical",fullyInterconnected=False)
        self.create_chain_mplex(n)
        self.assertEqual(diagnostics.degs(n,degstype="nodes"),{(1,1):2,(2,1):3,(3,1):3,(4,1):2,(1,3):2,(2,3):3,(3,3):3,(4,3):2})

        n=net.MultiplexNetwork(couplings="ordinal",fullyInterconnected=True)
        self.create_chain_mplex(n)
        self.assertEqual(diagnostics.degs(n,degstype="nodes"),{(1,1):2,(2,1):3,(3,1):3,(4,1):2,(1,3):2,(2,3):3,(3,3):3,(4,3):2,(1,2):2,(2,2):2,(3,2):2,(4,2):2})

        n=net.MultiplexNetwork(couplings="ordinal",fullyInterconnected=False)
        self.create_chain_mplex(n)
        self.assertEqual(diagnostics.degs(n,degstype="nodes"),{(1,1):1,(2,1):2,(3,1):2,(4,1):1,(1,3):1,(2,3):2,(3,3):2,(4,3):1})


    def test_dijkstra_monoplex(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=1
        n[1,3]=1
        n[2,3]=1
        n[2,4]=1
        n[3,4]=1
        n[3,5]=1

        d,f=diagnostics.dijkstra(n,[1])

        ftrue=net.MultilayerNetwork(aspects=0,fullyInterconnected=False,directed=True,noEdge=-1)
        ftrue[1,1]=0;ftrue[1,2]=1;ftrue[1,3]=1;ftrue[2,4]=1;ftrue[3,4]=1;ftrue[3,5]=1
        self.assertEqual(d,{1:0,2:1,3:1,4:2,5:2})
        self.assertEqual(f,ftrue)

        d,f=diagnostics.dijkstra(n,[1,2])
        ftrue=net.MultilayerNetwork(aspects=0,fullyInterconnected=False,directed=True,noEdge=-1)
        ftrue[1,1]=0;ftrue[2,2]=0;ftrue[1,3]=1;ftrue[2,3]=1;ftrue[2,4]=1;ftrue[3,5]=1
        self.assertEqual(d,{1:0,2:0,3:1,4:1,5:2})
        self.assertEqual(f,ftrue)

    def test_dijkstra_monoplex_compare(self):
        n=models.er(100,0.1)
        d,f=diagnostics.dijkstra(n,[1])
        
        self.assertEqual(d, nx.shortest_path_length(n,1))
        
    def test_dijkstra_multilayer_two_aspect(self):
        n=net.MultilayerNetwork(aspects=2,directed=True)
        n[1,'a',1][2,'a',2]=1
        n[2,'a',2][3,'a',3]=1
        n[3,'a',3][4,'a',4]=1
        n[1,'b',1.5][3,'b',2.5]=1

        n[1,'a',1][1,'b',1.25]=0.25
        n[1,'b',1.5][1,'a',1.75]=0.25
        n[3,'b',2.5][3,'a',2.75]=0.25

        n[1,'a',1.75][1,'a',2]=0.25
        n[1,'b',1.25][1,'b',1.5]=0.25
        n[3,'a',2.75][3,'a',3]=0.25


        d,f=diagnostics.dijkstra(n,[(1,'a',1)])
        #for nl,dist in d.iteritems():
        for nl in d:
            dist=d[nl]            
            self.assertEqual(d[nl],nl[2]-1)

        d,f=diagnostics.dijkstra_mlayer_prune(n,[(1,None,None)],aaspects=[1,2])
        self.assertEqual(d[(1,)],0)
        self.assertEqual(d[(2,)],1)
        self.assertEqual(d[(3,)],1)
        self.assertEqual(d[(4,)],2.5)
        ftrue=net.MultilayerNetwork(aspects=2,fullyInterconnected=False,directed=True,noEdge=-1)
        ftrue[1,'a',1][1,'a',1]=0; ftrue[1,'b',1.5][1,'b',1.5]=0;ftrue[1,'b',1.25][1,'b',1.25]=0; ftrue[1,'a',1.75][1,'a',1.75];ftrue[1,'a',2][1,'a',2]

        #print d,list(f.edges)

def test_diagnostics():
    suite = unittest.TestSuite()    
    suite.addTest(TestDiagnostics("test_monoplex_density_degs_mnet"))
    suite.addTest(TestDiagnostics("test_multiplex_density_degs_mnet"))
    suite.addTest(TestDiagnostics("test_multilayer_degs_multilayernet"))
    suite.addTest(TestDiagnostics("test_multilayer_degs_mplexnet"))
    suite.addTest(TestDiagnostics("test_dijkstra_monoplex"))
    suite.addTest(TestDiagnostics("test_dijkstra_monoplex_compare"))
    suite.addTest(TestDiagnostics("test_dijkstra_multilayer_two_aspect"))

    return unittest.TextTestRunner().run(suite).wasSuccessful() 

if __name__ == '__main__':
    sys.exit(not test_diagnostics())

