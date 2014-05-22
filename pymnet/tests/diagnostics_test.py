import unittest
import sys
sys.path.append("../../")

from pymnet import net,diagnostics


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


def test_diagnostics():
    suite = unittest.TestSuite()    
    suite.addTest(TestDiagnostics("test_monoplex_density_degs_mnet"))
    suite.addTest(TestDiagnostics("test_multiplex_density_degs_mnet"))
    suite.addTest(TestDiagnostics("test_multilayer_degs_multilayernet"))
    suite.addTest(TestDiagnostics("test_multilayer_degs_mplexnet"))

    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_diagnostics()

