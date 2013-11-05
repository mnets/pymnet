import unittest
from operator import itemgetter

import sys
sys.path.append("../../")
from pymnet import net
import pymnet
#from .. import net


class TestNet(unittest.TestCase):
    
    def setUp(self):
        pass

    ##### Test flat net

    def test_flat(self,net):
        net[1,2]=1
        net[2,3]=1

        #Overall structure with getter.
        self.assertEqual(net[1,2],1)
        self.assertEqual(net[2,1],1)
        self.assertEqual(net[2,3],1)
        self.assertEqual(net[3,2],1)
        self.assertEqual(net[1,3],0)
        self.assertEqual(net[1,999],0)

        #Iterators,degrees,strengths
        self.assertEqual(list(net[1]),[2])
        self.assertEqual(list(net[3]),[2])
        self.assertEqual(net[1].deg(),1)
        self.assertEqual(net[2].deg(),2)
        self.assertEqual(net[1].str(),1)
        self.assertEqual(net[2].str(),2)
        self.assertEqual(list(net[4]),[])

        #Test alternative notations
        self.assertEqual(net[1][2],1)

        #Test edge iterator
        self.assertEqual(len(list(net.edges)),2)
        self.assertTrue((1,2,1) or (2,1,1) in list(net.edges))
        self.assertTrue((2,3,1) or (3,2,1) in list(net.edges))

        #Modify and repeat previous tests
        net[1,2]=0 #Removes the edge
        net[1,3]=1

        self.assertEqual(net[1,2],0)
        self.assertEqual(net[2,1],0)
        self.assertEqual(net[2,3],1)
        self.assertEqual(net[3,2],1)
        self.assertEqual(net[1,3],1)

        self.assertEqual(list(net[1]),[3])
        self.assertEqual(set(net[3]),set([1,2]))
        self.assertEqual(net[1].deg(),1)
        self.assertEqual(net[2].deg(),1)
        self.assertEqual(net[1].str(),1)
        self.assertEqual(net[2].str(),1)
        self.assertEqual(list(net[4]),[])

        self.assertEqual(net[1][2],0)

        self.assertEqual(len(list(net.edges)),2)
        self.assertTrue((1,3,1) or (3,1,1) in list(net.edges))
        self.assertTrue((2,3,1) or (3,2,1) in list(net.edges))

        self.assertEqual(net[4].deg(),0) #missing node


    def test_flat_directed(self,net):
        net[1,2]=1
        net[2,1]=1
        net[2,3]=1

        #Overall structure with getter.
        self.assertEqual(net[1,2],1)
        self.assertEqual(net[2,1],1)
        self.assertEqual(net[2,3],1)
        self.assertEqual(net[3,2],0)
        self.assertEqual(net[1,3],0)
        self.assertEqual(net[1,999],0)

        #Iterators,degrees,strengths
        self.assertEqual(list(net[1]),[2])
        self.assertEqual(set(net[2]),set([1,3]))
        self.assertEqual(list(net[3]),[])
        self.assertEqual(net[1].deg(),1)
        self.assertEqual(net[2].deg(),2)
        self.assertEqual(net[1].str(),1)
        self.assertEqual(net[2].str(),2)
        self.assertEqual(list(net[4]),[])

        #Test alternative notations
        self.assertEqual(net[1][2],1)
        self.assertEqual(net[2][1],1)
        self.assertEqual(net[3][2],0)

        #Test edge iterator
        self.assertEqual(len(list(net.edges)),3)
        self.assertTrue((1,2,1) in list(net.edges))
        self.assertTrue((2,1,1) in list(net.edges))
        self.assertTrue((2,3,1) in list(net.edges))

        #Modify and repeat previous tests
        net[1,2]=0 #Removes the edge
        net[1,3]=1
        # Network structure after this:
        # net[1,2] == 0, net[2,1] == 1
        # net[2,3] == 1, net[3,2] == 0
        # net[1,3] == 1, net[3,1] == 0

        self.assertEqual(net[1,2],0)
        self.assertEqual(net[2,1],1)
        self.assertEqual(net[2,3],1)
        self.assertEqual(net[3,2],0)
        self.assertEqual(net[1,3],1)
        self.assertEqual(net[3,1],0)

        self.assertEqual(list(net[1]),[3])
        self.assertEqual(set(net[2]),set([1,3]))
        self.assertEqual(list(net[3]),[])

        self.assertEqual(net[1].deg(),2)
        self.assertEqual(net[2].deg(),2)
        self.assertEqual(net[3].deg(),2)
        self.assertEqual(net[1].str(),2)
        self.assertEqual(net[2].str(),2)
        self.assertEqual(net[3].str(),2)
        self.assertEqual(list(net[4]),[])

        self.assertEqual(net[1][2],0)

        self.assertEqual(len(list(net.edges)),3)
        self.assertTrue((2,1,1) in list(net.edges))
        self.assertTrue((2,3,1) in list(net.edges))
        self.assertTrue((1,3,1) in list(net.edges))

        self.assertEqual(net[4].deg(),0) #missing node


    def test_flat_directed_mnet(self):
        testnet=net.MultilayerNetwork(aspects=0,directed=True)
        self.test_flat(testnet)

    def test_flat_mnet(self):
        testnet=net.MultilayerNetwork(aspects=0)
        self.test_flat(testnet)

    ##### Test simple couplings

    def test_simple_couplings(self,net,hasDiagonalLinks=False):
        """Tests basic functionality of Multiplex networks with two layers.

        The input network must have connections between nodes i,i,s,s, where
        i is in {1,2,3} and s is in {1,2}.
        """
        #First, we add some links
        if not hasDiagonalLinks:
            net[1,2,1]=1
            net[2,1][3,1]=1#net[2,3,1]=1
            net[1,2,2]=1
            net[1,3,2]=1

        #Test the lattice
        self.assertEqual(net[1,1,1,2],1)
        self.assertEqual(net[1,1,2,1],1)
        self.assertEqual(net[1,2,1,2],0)

        #Tests for network structure
        self.assertEqual(net[1,2,1,1],1)
        self.assertEqual(net[2,1,1,1],1)
        self.assertEqual(net[2,3,1,1],1)
        self.assertEqual(net[3,2,1,1],1)
        self.assertEqual(net[1,2,2,2],1)
        self.assertEqual(net[2,1,2,2],1)
        self.assertEqual(net[1,3,2,2],1)
        self.assertEqual(net[3,1,2,2],1)

        #TODO: Tests for missing links, inside and outside network

        #TODO: Tests for alternative notations

        #Tests for node iterators
        self.assertEqual(set(net[1,1]),set([(1,2),(2,1)]))
        self.assertEqual(set(net[1,:,1,:]),set([(1,2),(2,1)]))
        self.assertEqual(list(net[1,:,1,1]),[(2,1)])
        self.assertEqual(list(net[1,1,1,:]),[(1,2)])
        self.assertEqual(list(net[4,:,1,1]),[])

        #TODO: Tests for degrees and strength

        #TODO: Tests for iterating over nodes and layers
        self.assertEqual(set(net.slices[0]),set([1,2,3]))
        self.assertEqual(set(net.slices[1]),set([1,2]))

        #TODO: Add tests for removing links by setting them to 0


    def test_simple_couplings_mnet(self):
        testnet=net.MultilayerNetwork(aspects=1)
        testnet[1,1,1,2]=1
        testnet[2,2,1,2]=1
        testnet[3,3,1,2]=1
        self.test_simple_couplings(testnet)

    def test_simple_couplings_categorical_mplex(self):
        testnet=net.MultiplexNetwork(couplings=[('categorical',1.0)])
        self.test_simple_couplings(testnet)

        testnet=net.MultiplexNetwork(couplings=['categorical'])
        self.test_simple_couplings(testnet)

        testnet=net.MultiplexNetwork(couplings=('categorical',1.0))
        self.test_simple_couplings(testnet)

        testnet=net.MultiplexNetwork(couplings='categorical')
        self.test_simple_couplings(testnet)

    def test_simple_couplings_ordinal_mplex(self):
        testnet=net.MultiplexNetwork(couplings=[('ordinal',1.0)])
        self.test_simple_couplings(testnet)

    def test_simple_couplings_cmnet_add_to_A(self):
        """test_simple_couplings with links added to the net.A matrices directly.
        """
        n=net.MultiplexNetwork(couplings=[('categorical',1.0)])
        n.add_layer(1,1)
        n.add_layer(2,1)
        n.A[1][1][2]=1
        n.A[1][2,3]=1
        n.A[2][1,2]=1
        n.A[2][1,3]=1
        self.test_simple_couplings(n,hasDiagonalLinks=True)

    ##### Test ordinal couplings

    def test_ordinal_couplings(self,net):
        """Run several tests to see if the network is ordinally coupled.
        
        The given net must be empty and nodes 1,2,3 ordinally coupled in layers
        1,2,3.
        """
        #First, we add some links
        net[1,2,1]=1
        net[2,1][3,1]=1#net[2,3,1]=1
        net[1,2,2]=1
        net[1,3,2]=1
        net[1,2,3]=1
        
        #Test the lattice
        self.assertEqual(net[1,1,1,2],1)
        self.assertEqual(net[1,1,2,1],1)
        self.assertEqual(net[1,1,2,3],1)
        self.assertEqual(net[1,1,1,3],0)
        self.assertEqual(net[1,2,1,2],0)

        #Tests for node iterators
        self.assertEqual(set(net[1,1]),set([(1,2),(2,1)]))
        self.assertEqual(set(net[1,2]),set([(1,1),(1,3),(2,2),(3,2)]))
        self.assertEqual(set(net[1,3]),set([(1,2),(2,3)]))
        self.assertEqual(set(net[1,:,1,:]),set([(1,2),(2,1)]))
        self.assertEqual(list(net[1,:,1,1]),[(2,1)])
        self.assertEqual(list(net[1,1,1,:]),[(1,2)])
        self.assertEqual(set(net[1,1,2,:]),set([(1,1),(1,3)]))
        self.assertEqual(list(net[4,:,1,1]),[])

        #Tests for degs
        self.assertEqual(net[1,1].deg(),2)
        self.assertEqual(net[1,2].deg(),4)
        self.assertEqual(net[1,3].deg(),2)
        self.assertEqual(net[1,:,1,:].deg(),2)
        self.assertEqual(net[1,:,1,1].deg(),1)
        self.assertEqual(net[1,1,1,:].deg(),1)
        self.assertEqual(net[1,1,2,:].deg(),2)
        self.assertEqual(net[4,:,1,1].deg(),0)


    def test_ordinal_couplings_mplex(self):
        """Test the ordinal couplings in the MultiplexNetwork class.
        """
        testnet=net.MultiplexNetwork(couplings=[('ordinal',1.0)])
        self.test_ordinal_couplings(testnet)

    def test_ordinal_couplings_mlayer(self):
        """Testing the ordinal couplings by explicitely constructing them
        in MultilayerNetwork. This is more like a test of the test.
        """
        testnet=net.MultilayerNetwork(aspects=1)
        testnet[1,1,1,2]=1
        testnet[1,1,2,3]=1
        testnet[2,2,1,2]=1
        testnet[2,2,2,3]=1
        testnet[3,3,1,2]=1
        testnet[3,3,2,3]=1
        self.test_ordinal_couplings(testnet)

    ##### Test couplings

    def test_network_coupling(self,net):
        net[1,2,'a']=1
        net[2,3,'a']=1
        net[1,2,'b']=1
        net[1,3,'b']=1

        self.assertEqual(net[1,1,'a','b'],1)
        self.assertEqual(net[1,1,'a','c'],0)
        self.assertEqual(net[1,1,'b','c'],1)

        self.assertEqual(net[1,1,'a','d'],0) #d not in net



    def test_network_coupling_mnet(self):
        testnet=net.MultilayerNetwork(aspects=1)
        testnet[1,1,'a','b']=1
        testnet[2,2,'a','b']=1
        testnet[3,3,'a','b']=1
        testnet[1,1,'a','c']=0
        testnet[2,2,'a','c']=0
        testnet[3,3,'a','c']=0
        testnet[1,1,'b','c']=1
        testnet[2,2,'b','c']=1
        testnet[3,3,'b','c']=1
        self.test_network_coupling(testnet)
        
    def test_network_coupling_cmnet(self):
        couplingNet=net.MultilayerNetwork(aspects=0)
        couplingNet['a','b']=1
        couplingNet['a','c']=0
        couplingNet['b','c']=1
        testnet=net.MultiplexNetwork(couplings=[couplingNet])
        self.test_network_coupling(testnet)


    def add_intralayer_edges_2dim(self,net):
        net[1,2,'a','x']=3
        net[2,3,'a','x']=1
        net[1,2,'b','x']=1
        net[1,3,'b','x']=1
        net[1,2,'c','x']=1
        net[1,3,'c','x']=1
        net[2,3,'c','x']=1

        net[1,2,'b','y']=1
        net[2,3,'b','y']=1
        net[1,2,'c','y']=1
        net[1,3,'c','y']=1
        net[1,2,'a','y']=1
        net[1,3,'a','y']=1
        net[2,3,'a','y']=1

    def test_2dim_categorical_couplings(self,net):
        #Test existing edges
        self.assertEqual(net[1,2,'a','a','x','x'],3)
        self.assertEqual(net[1,1,'a','b','x','x'],1)
        self.assertEqual(net[1,1,'a','a','x','y'],1)
        
        #Test missing edges
        self.assertEqual(net[1,2,'a','b','x','x'],0)
        self.assertEqual(net[1,2,'a','b','x','y'],0)
        self.assertEqual(net[1,1,'a','b','x','y'],0)

        #Test iterators
        self.assertEqual(set(net[1,'a','x']),set([(2,'a','x'),(1,'b','x'),(1,'c','x'),(1,'a','y')]))
        self.assertEqual(set(net[1,:,'a','a','x','x']),set([(2,'a','x')]))
        self.assertEqual(set(net[1,1,'a',:,'x','x']),set([(1,'b','x'),(1,'c','x')]))
        self.assertEqual(set(net[1,1,'a','a','x',:]),set([(1,'a','y')]))
        self.assertEqual(set(net[1,:,'a',:,'x','x']),set([(2,'a','x'),(1,'b','x'),(1,'c','x')]))
        self.assertEqual(set(net[1,:,'a','a','x',:]),set([(2,'a','x'),(1,'a','y')]))
        self.assertEqual(set(net[1,1,'a',:,'x',:]),set([(1,'b','x'),(1,'c','x'),(1,'a','y')]))

        #Test degs
        self.assertEqual(net[1,'a','x'].deg(),4)
        self.assertEqual(net[1,:,'a','a','x','x'].deg(),1)
        self.assertEqual(net[1,1,'a',:,'x','x'].deg(),2)
        self.assertEqual(net[1,1,'a','a','x',:].deg(),1)
        self.assertEqual(net[1,:,'a',:,'x','x'].deg(),3)
        self.assertEqual(net[1,:,'a','a','x',:].deg(),2)
        self.assertEqual(net[1,1,'a',:,'x',:].deg(),3)

        #Test strengths
        self.assertEqual(net[1,'a','x'].str(),6)
        self.assertEqual(net[1,:,'a','a','x','x'].str(),3)
        self.assertEqual(net[1,1,'a',:,'x','x'].str(),2)
        self.assertEqual(net[1,1,'a','a','x',:].str(),1)
        self.assertEqual(net[1,:,'a',:,'x','x'].str(),5)
        self.assertEqual(net[1,:,'a','a','x',:].str(),4)
        self.assertEqual(net[1,1,'a',:,'x',:].str(),3)

        #Test edge iterator
        self.assertEqual(len(list(net.edges)),41)



    def test_2dim_categorical_couplings_mnet(self): 
        testnet=net.MultilayerNetwork(aspects=2)
        testnet[1,1,'a','b','x','x']=1
        testnet[2,2,'a','b','x','x']=1
        testnet[3,3,'a','b','x','x']=1
        testnet[1,1,'a','c','x','x']=1
        testnet[2,2,'a','c','x','x']=1
        testnet[3,3,'a','c','x','x']=1
        testnet[1,1,'c','b','x','x']=1
        testnet[2,2,'c','b','x','x']=1
        testnet[3,3,'c','b','x','x']=1

        testnet[1,1,'a','b','y','y']=1
        testnet[2,2,'a','b','y','y']=1
        testnet[3,3,'a','b','y','y']=1
        testnet[1,1,'a','c','y','y']=1
        testnet[2,2,'a','c','y','y']=1
        testnet[3,3,'a','c','y','y']=1
        testnet[1,1,'c','b','y','y']=1
        testnet[2,2,'c','b','y','y']=1
        testnet[3,3,'c','b','y','y']=1

        testnet[1,1,'a','a','x','y']=1
        testnet[2,2,'a','a','x','y']=1
        testnet[3,3,'a','a','x','y']=1

        testnet[1,1,'b','b','x','y']=1
        testnet[2,2,'b','b','x','y']=1
        testnet[3,3,'b','b','x','y']=1

        testnet[1,1,'c','c','x','y']=1
        testnet[2,2,'c','c','x','y']=1
        testnet[3,3,'c','c','x','y']=1

        self.add_intralayer_edges_2dim(testnet)

        self.test_2dim_categorical_couplings(testnet)

    def test_2dim_categorical_couplings_cmnet(self):
        testnet=net.MultiplexNetwork(couplings=[('categorical',1.0),('categorical',1.0)])
        self.add_intralayer_edges_2dim(testnet)
        self.test_2dim_categorical_couplings(testnet)


    def test_multiplex_diagonal_notation(self):
        n=net.MultiplexNetwork(couplings=[('categorical',1.0)])
        n.add_layer(1,1)
        n[1,2,1]=1
        n[1,2,2]=1
        
        #test iterator consistency
        for layer in n.slices[1]:
            n.A[layer]

        self.assertEqual(n.A[1][1,2],1)
        self.assertEqual(n.A[2][1,2],1)

    #TODO: tests for noEdge parameter

        
    def test_simple_couplings_cmnet_nonglobalnodes(self):
        """ Test that MultiplexNetwork fullyInterconnected parameter
        is working as it is supposed.
        """
        n=net.MultiplexNetwork(couplings=[('categorical',1.0)],fullyInterconnected=False)

        #Add three layers to the network
        n.add_layer('a',1)
        n.add_layer('b',1)
        n.add_layer('c',1)

        #Implicitely add nodes 1, 2 and 3 to the networks
        n.A['a'][1,2]=1
        n.A['b'][1,2]=1
        n.A['c'][2,3]=1
        
        #Explicitely add nodes 4 and 5 to the networks
        n.A['a'].add_node(4)
        n.A['b'].add_node(4)
        n.A['a'].add_node(5)
        n.A['b'].add_node(5)
        n.A['c'].add_node(5)

        #Tests for edge getters
        self.assertEqual(n[1,1,'a','b'],1)
        self.assertEqual(n[1,1,'a','c'],0)
        self.assertEqual(n[1,1,'b','c'],0)
        self.assertEqual(n[2,2,'a','b'],1)
        self.assertEqual(n[2,2,'a','c'],1)
        self.assertEqual(n[2,2,'b','c'],1)
        self.assertEqual(n[3,3,'a','b'],0)
        self.assertEqual(n[3,3,'a','c'],0)
        self.assertEqual(n[3,3,'b','c'],0)
        
        self.assertEqual(n[4,4,'a','b'],1)
        self.assertEqual(n[4,4,'a','c'],0)
        self.assertEqual(n[4,4,'b','c'],0)
        self.assertEqual(n[5,5,'a','b'],1)
        self.assertEqual(n[5,5,'a','c'],1)
        self.assertEqual(n[5,5,'b','c'],1)

        #Tests for iterators
        self.assertEqual(set(n[1,1,'a',:]),set([(1,'b')]))
        self.assertEqual(set(n[2,2,'a',:]),set([(2,'b'),(2,'c')]))
        self.assertEqual(set(n[3,3,'a',:]),set([]))
        self.assertEqual(set(n[1,1,'b',:]),set([(1,'a')]))
        self.assertEqual(set(n[2,2,'b',:]),set([(2,'a'),(2,'c')]))
        self.assertEqual(set(n[3,3,'b',:]),set([]))
        self.assertEqual(set(n[1,1,'c',:]),set([]))
        self.assertEqual(set(n[2,2,'c',:]),set([(2,'a'),(2,'b')]))
        self.assertEqual(set(n[3,3,'c',:]),set([]))

        self.assertEqual(set(n[4,4,'a',:]),set([(4,'b')]))
        self.assertEqual(set(n[5,5,'a',:]),set([(5,'b'),(5,'c')]))
        self.assertEqual(set(n[4,4,'b',:]),set([(4,'a')]))
        self.assertEqual(set(n[5,5,'b',:]),set([(5,'a'),(5,'c')]))
        self.assertEqual(set(n[4,4,'c',:]),set([]))
        self.assertEqual(set(n[5,5,'c',:]),set([(5,'a'),(5,'b')]))

        #Tests for deg,str
        self.assertEqual(n[1,1,'a',:].deg(),1)
        self.assertEqual(n[2,2,'a',:].deg(),2)
        self.assertEqual(n[3,3,'a',:].deg(),0)
        self.assertEqual(n[1,1,'b',:].deg(),1)
        self.assertEqual(n[2,2,'b',:].deg(),2)
        self.assertEqual(n[3,3,'b',:].deg(),0)
        self.assertEqual(n[1,1,'c',:].deg(),0)
        self.assertEqual(n[2,2,'c',:].deg(),2)
        self.assertEqual(n[3,3,'c',:].deg(),0)

        self.assertEqual(n[4,4,'a',:].deg(),1)
        self.assertEqual(n[5,5,'a',:].deg(),2)
        self.assertEqual(n[4,4,'b',:].deg(),1)
        self.assertEqual(n[5,5,'b',:].deg(),2)
        self.assertEqual(n[4,4,'c',:].deg(),0)
        self.assertEqual(n[5,5,'c',:].deg(),2)

        self.assertEqual(n[1,1,'a',:].str(),1)
        self.assertEqual(n[2,2,'a',:].str(),2)
        self.assertEqual(n[3,3,'a',:].str(),0)
        self.assertEqual(n[1,1,'b',:].str(),1)
        self.assertEqual(n[2,2,'b',:].str(),2)
        self.assertEqual(n[3,3,'b',:].str(),0)
        self.assertEqual(n[1,1,'c',:].str(),0)
        self.assertEqual(n[2,2,'c',:].str(),2)
        self.assertEqual(n[3,3,'c',:].str(),0)

        self.assertEqual(n[4,4,'a',:].str(),1)
        self.assertEqual(n[5,5,'a',:].str(),2)
        self.assertEqual(n[4,4,'b',:].str(),1)
        self.assertEqual(n[5,5,'b',:].str(),2)
        self.assertEqual(n[4,4,'c',:].str(),0)
        self.assertEqual(n[5,5,'c',:].str(),2)



def test_net():
    suite = unittest.TestSuite()    
    suite.addTest(TestNet("test_flat_mnet"))
    #suite.addTest(TestNet("test_flat_directed_mnet"))
    suite.addTest(TestNet("test_simple_couplings_mnet"))
    suite.addTest(TestNet("test_simple_couplings_categorical_mplex"))
    suite.addTest(TestNet("test_simple_couplings_ordinal_mplex"))
    suite.addTest(TestNet("test_simple_couplings_cmnet_add_to_A"))
    suite.addTest(TestNet("test_2dim_categorical_couplings_mnet"))
    suite.addTest(TestNet("test_2dim_categorical_couplings_cmnet"))
    suite.addTest(TestNet("test_network_coupling_mnet"))
    suite.addTest(TestNet("test_network_coupling_cmnet"))
    suite.addTest(TestNet("test_multiplex_diagonal_notation"))
    suite.addTest(TestNet("test_simple_couplings_cmnet_nonglobalnodes"))
    suite.addTest(TestNet("test_ordinal_couplings_mplex"))
    suite.addTest(TestNet("test_ordinal_couplings_mlayer"))
    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_net()

