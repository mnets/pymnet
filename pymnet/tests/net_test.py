import unittest
from operator import itemgetter

import sys
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
        self.assertEqual(net[3].deg(),1)
        self.assertEqual(net[1].str(),1)
        self.assertEqual(net[2].str(),2)
        self.assertEqual(net[3].str(),1)
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

        #Test that net works as directed net too
        self.assertEqual(list(net[1].iter_out()),[3])
        self.assertEqual(set(net[3].iter_out()),set([1,2]))
        self.assertEqual(net[1].deg_out(),1)
        self.assertEqual(net[2].deg_out(),1)
        self.assertEqual(net[1].str_out(),1)
        self.assertEqual(net[2].str_out(),1)
        self.assertEqual(list(net[4].iter_out()),[])

        self.assertEqual(list(net[1].iter_in()),[3])
        self.assertEqual(set(net[3].iter_in()),set([1,2]))
        self.assertEqual(net[1].deg_in(),1)
        self.assertEqual(net[2].deg_in(),1)
        self.assertEqual(net[1].str_in(),1)
        self.assertEqual(net[2].str_in(),1)
        self.assertEqual(list(net[4].iter_in()),[])

        self.assertEqual(list(net[1].iter_total()),[3])
        self.assertEqual(set(net[3].iter_total()),set([1,2]))
        self.assertEqual(net[1].deg_total(),1)
        self.assertEqual(net[2].deg_total(),1)
        self.assertEqual(net[1].str_total(),1)
        self.assertEqual(net[2].str_total(),1)
        self.assertEqual(list(net[4].iter_total()),[])
        

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
        self.assertEqual(list(net[3]),[2])
        self.assertEqual(net[1].deg(),1)
        self.assertEqual(net[2].deg(),2)
        self.assertEqual(net[3].deg(),1)
        self.assertEqual(net[1].str(),2)
        self.assertEqual(net[2].str(),3)
        self.assertEqual(net[3].str(),1)
        self.assertEqual(list(net[4]),[])

        self.assertEqual(list(net[1].iter_total()),[2])
        self.assertEqual(set(net[2].iter_total()),set([1,3]))
        self.assertEqual(list(net[3].iter_total()),[2])
        self.assertEqual(net[1].deg_total(),1)
        self.assertEqual(net[2].deg_total(),2)
        self.assertEqual(net[3].deg_total(),1)
        self.assertEqual(net[1].str_total(),2)
        self.assertEqual(net[2].str_total(),3)
        self.assertEqual(net[3].str_total(),1)
        self.assertEqual(list(net[4].iter_total()),[])

        self.assertEqual(list(net[1].iter_in()),[2])
        self.assertEqual(set(net[2].iter_in()),set([1]))
        self.assertEqual(list(net[3].iter_in()),[2])
        self.assertEqual(net[1].deg_in(),1)
        self.assertEqual(net[2].deg_in(),1)
        self.assertEqual(net[3].deg_in(),1)
        self.assertEqual(net[1].str_in(),1)
        self.assertEqual(net[2].str_in(),1)
        self.assertEqual(net[3].str_in(),1)
        self.assertEqual(list(net[4].iter_in()),[])

        self.assertEqual(list(net[1].iter_out()),[2])
        self.assertEqual(set(net[2].iter_out()),set([1,3]))
        self.assertEqual(list(net[3].iter_out()),[])
        self.assertEqual(net[1].deg_out(),1)
        self.assertEqual(net[2].deg_out(),2)
        self.assertEqual(net[3].deg_out(),0)
        self.assertEqual(net[1].str_out(),1)
        self.assertEqual(net[2].str_out(),2)
        self.assertEqual(net[3].str_out(),0)
        self.assertEqual(list(net[4].iter_out()),[])

        #Test alternative notations
        self.assertEqual(net[1][2],1)
        self.assertEqual(net[2][1],1)
        self.assertEqual(net[3][2],0)

        #Test edge iterator
        self.assertEqual(len(list(net.edges)),3)
        self.assertEqual(len(net.edges),3)
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

        self.assertEqual(set(net[1]),set([2,3]))
        self.assertEqual(set(net[2]),set([1,3]))
        self.assertEqual(set(net[3]),set([1,2]))
        self.assertEqual(list(net[4]),[])

        self.assertEqual(net[1].deg(),2)
        self.assertEqual(net[2].deg(),2)
        self.assertEqual(net[3].deg(),2)
        self.assertEqual(net[1].str(),2)
        self.assertEqual(net[2].str(),2)
        self.assertEqual(net[3].str(),2)

        self.assertEqual(set(net[1].iter_total()),set([2,3]))
        self.assertEqual(set(net[2].iter_total()),set([1,3]))
        self.assertEqual(set(net[3].iter_total()),set([1,2]))
        self.assertEqual(list(net[4].iter_total()),[])

        self.assertEqual(net[1].deg_total(),2)
        self.assertEqual(net[2].deg_total(),2)
        self.assertEqual(net[3].deg_total(),2)
        self.assertEqual(net[1].str_total(),2)
        self.assertEqual(net[2].str_total(),2)
        self.assertEqual(net[3].str_total(),2)

        self.assertEqual(set(net[1].iter_in()),set([2]))
        self.assertEqual(set(net[2].iter_in()),set([]))
        self.assertEqual(set(net[3].iter_in()),set([1,2]))
        self.assertEqual(list(net[4].iter_in()),[])

        self.assertEqual(net[1].deg_in(),1)
        self.assertEqual(net[2].deg_in(),0)
        self.assertEqual(net[3].deg_in(),2)
        self.assertEqual(net[1].str_in(),1)
        self.assertEqual(net[2].str_in(),0)
        self.assertEqual(net[3].str_in(),2)

        self.assertEqual(set(net[1].iter_out()),set([3]))
        self.assertEqual(set(net[2].iter_out()),set([1,3]))
        self.assertEqual(set(net[3].iter_out()),set([]))
        self.assertEqual(list(net[4].iter_out()),[])

        self.assertEqual(net[1].deg_out(),1)
        self.assertEqual(net[2].deg_out(),2)
        self.assertEqual(net[3].deg_out(),0)
        self.assertEqual(net[1].str_out(),1)
        self.assertEqual(net[2].str_out(),2)
        self.assertEqual(net[3].str_out(),0)

        self.assertEqual(net[1][2],0)

        self.assertEqual(len(list(net.edges)),3)
        self.assertTrue((2,1,1) in list(net.edges))
        self.assertTrue((2,3,1) in list(net.edges))
        self.assertTrue((1,3,1) in list(net.edges))

        self.assertEqual(net[4].deg(),0) #missing node


    def test_flat_directed_mnet(self):
        testnet=net.MultilayerNetwork(aspects=0,directed=True)
        self.test_flat_directed(testnet)

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

        #Test the listing the nodes in intra-layer networks
        self.assertEqual(set(n.A['a']),set([1,2,4,5]))
        self.assertEqual(set(n.A['b']),set([1,2,4,5]))
        self.assertEqual(set(n.A['c']),set([2,3,5]))

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

    def test_flat_equal(self):
        n1=net.MultilayerNetwork(aspects=0)
        n2=net.MultilayerNetwork(aspects=0)
        self.assertTrue(n1==n2)
        n1[1,2]=1
        self.assertTrue(n1!=n2)
        n2[1,2]=1.0
        self.assertTrue(n1==n2)
        n1.add_node(3)
        self.assertTrue(n1!=n2)

    def test_2dim_equal(self):
        n1=net.MultilayerNetwork(aspects=2)
        n2=net.MultilayerNetwork(aspects=2)
        self.assertTrue(n1==n2)
        n1[1,2,'a','x']=1
        self.assertTrue(n1!=n2)
        n2[1,2,'a','x']=1
        self.assertTrue(n1==n2)
        n1.add_node(3)
        self.assertTrue(n1!=n2)

    def test_mplex_equal(self):
        n1=net.MultiplexNetwork(couplings=["categorical","categorical"])
        n2=net.MultiplexNetwork(couplings=["categorical","categorical"])
        n3=net.MultiplexNetwork(couplings=["categorical","none"])
        self.assertTrue(n1==n2)
        self.assertTrue(n1!=n3)
        n1[1,2,'a','x']=1
        self.assertTrue(n1!=n2)
        n2[1,2,'a','x']=1
        self.assertTrue(n1==n2)
        n1.add_node(3)
        self.assertTrue(n1!=n2)

    def test_node_iterators_mlayer(self,empty_net,net_type="mlayer"):
        """ Tests node iterators (iter_nodes, iter_node_layers). 

        Empty network with 0, 1 or 2 aspects must be given as an input. The 
        network can be node-aligned or not.
        """
        n=empty_net
        if n.aspects==0:
            n.add_node(1)
            n.add_node(2)
            n[3,4]=1
            self.assertEqual(set(n.iter_nodes()),set([1,2,3,4]))
        elif n.aspects==1:
            n.add_layer(1)
            n.add_layer(2)
            n.add_node(4,layer=1)
            n.add_node(5,layer=1)
            n.add_node(6,layer=2)
            n.add_node(7,layer=2)
            n[4,7,1]=1
            n[7,8,3]=1
            if net_type=="mlayer":
                n[9,10,1,2]=1
            elif net_type=="mplex":
                n.A[1].add_node(9)
                n.A[2][10,7]=1

            if n.fullyInterconnected:
                for l in range(1,4):
                    self.assertEqual(set(n.iter_nodes(layer=l)),set([4,5,6,7,8,9,10]))
            else:
                self.assertEqual(set(n.iter_nodes(layer=1)),set([4,5,7,9]))
                self.assertEqual(set(n.iter_nodes(layer=2)),set([6,7,10]))
                self.assertEqual(set(n.iter_nodes(layer=3)),set([7,8]))

        elif n.aspects==2:
            pass
        else:
            raise Exception()

    def test_node_iterators_all(self):
        """ Tests node iterators (iter_nodes, iter_node_layers) for all network types. """
        self.test_node_iterators_mlayer(net.MultilayerNetwork(aspects=0))
        self.test_node_iterators_mlayer(net.MultilayerNetwork(aspects=1,fullyInterconnected=True))
        self.test_node_iterators_mlayer(net.MultilayerNetwork(aspects=1,fullyInterconnected=False))
        self.test_node_iterators_mlayer(net.MultilayerNetwork(aspects=2,fullyInterconnected=True))
        self.test_node_iterators_mlayer(net.MultilayerNetwork(aspects=2,fullyInterconnected=False))

        """
        self.test_node_iterators(net.MultiplexNetwork(couplings='none',fullyInterconnected=True),net_type="mplex")
        self.test_node_iterators(net.MultiplexNetwork(couplings='none',fullyInterconnected=False),net_type="mplex")
        self.test_node_iterators(net.MultiplexNetwork(couplings=['none','none'],fullyInterconnected=True),net_type="mplex")
        self.test_node_iterators(net.MultiplexNetwork(couplings=['none','none'],fullyInterconnected=False),net_type="mplex")
        """

    def test_mplex_intralayer_nets(self):
        n=net.MultiplexNetwork(fullyInterconnected=True)
        n[1,2,"a"]=1
        n.A["a"].add_node(3)
        n[4,5,"b"]=1
        n.A["b"].add_node(6)

        self.assertEqual(set(n.A["a"]),set([1,2,3,4,5,6]))
        self.assertEqual(set(n.A["b"]),set([1,2,3,4,5,6]))

    def test_mlayer_2dim_nonglobalnodes(self):
        n=net.MultilayerNetwork(aspects=2,directed=True,fullyInterconnected=False)
        n[1,2,'a','b','t1','t2']=1
        n.add_node(3,('b','t1'))
        n.add_node(3,('b','t2'))
        self.assertEqual(n[1,2,'a','b','t2','t1'],0)
        self.assertEqual(n[1,2,'a','b','t1','t2'],1)
        self.assertEqual(n[1,'a','t1'].deg(),1)
        self.assertEqual(list(n[1,'a','t1']),[(2,'b','t2')])
        self.assertEqual(set(n.iter_nodes()),set([1,2,3]))
        self.assertEqual(set(n.iter_nodes(layer=('a','t1'))),set([1]))
        self.assertEqual(set(n.iter_nodes(layer=('b','t1'))),set([3]))
        self.assertEqual(set(n.iter_nodes(layer=('b','t2'))),set([2,3]))
        self.assertEqual(set(n.iter_nodes(layer=('a','t2'))),set([]))
        self.assertEqual(set(n.iter_node_layers()),set([(1, 'a', 't1'), (2, 'b', 't2'),(3, 'b', 't2'),(3, 'b', 't1')]))
        self.assertEqual(set(n.iter_layers(aspect=1)),set(['a','b']))
        self.assertEqual(set(n.iter_layers(aspect=2)),set(['t1','t2']))

    def test_mplex_adding_intralayer_nets(self):
        #some monoplex networks
        mono1=net.MultilayerNetwork(aspects=0)
        mono1[1,2]=1
        mono1[2,3]=1

        mono2=net.MultilayerNetwork(aspects=0)
        mono2[3,4]=1
        mono2[4,5]=1

        #single aspect, not fully interconnected.
        mnet=net.MultiplexNetwork(directed=False,fullyInterconnected=False)
        mnet.add_layer("a")
        mnet.add_layer("b")
        mnet.intranets["a"]=mono1
        self.assertEqual(sorted(mnet.intranets["a"].edges),sorted(mono1.edges))
        self.assertEqual(set(mnet.intranets["a"]),set([1,2,3]))
        
        mnet.intranets["b"]=mono2
        self.assertEqual(sorted(mnet.intranets["b"].edges),sorted(mono2.edges))
        self.assertEqual(set(mnet.intranets["b"]),set([3,4,5]))
        self.assertEqual(sorted(mnet.intranets["a"].edges),sorted(mono1.edges))
        self.assertEqual(set(mnet.intranets["a"]),set([1,2,3]))
 
        #single aspect, fully interconnected.
        mnet=net.MultiplexNetwork(directed=False,fullyInterconnected=True)
        mnet.add_layer("a")
        mnet.add_layer("b")
        mnet.intranets["a"]=mono1
        self.assertEqual(sorted(mnet.intranets["a"].edges),sorted(mono1.edges))
        self.assertEqual(set(mnet.intranets["a"]),set([1,2,3]))
        
        mnet.intranets["b"]=mono2
        self.assertEqual(sorted(mnet.intranets["b"].edges),sorted(mono2.edges))
        self.assertEqual(set(mnet.intranets["b"]),set([1,2,3,4,5]))
        self.assertEqual(sorted(mnet.intranets["a"].edges),sorted(mono1.edges))
        self.assertEqual(set(mnet.intranets["a"]),set([1,2,3,4,5]))

 
        #two aspects, not fully interconnected.
        mnet=net.MultiplexNetwork([None,None],directed=False,fullyInterconnected=False)
        mnet.add_layer("a",1)
        mnet.add_layer("b",1)
        mnet.add_layer("x",2)
        mnet.intranets["a","x"]=mono1
        self.assertEqual(sorted(mnet.intranets["a","x"].edges),sorted(mono1.edges))
        self.assertEqual(set(mnet.intranets["a","x"]),set([1,2,3]))
        
        mnet.intranets["b","x"]=mono2
        self.assertEqual(sorted(mnet.intranets["b","x"].edges),sorted(mono2.edges))
        self.assertEqual(set(mnet.intranets["b","x"]),set([3,4,5]))
        self.assertEqual(sorted(mnet.intranets["a","x"].edges),sorted(mono1.edges))
        self.assertEqual(set(mnet.intranets["a","x"]),set([1,2,3]))
 
        #two aspects, fully interconnected.
        mnet=net.MultiplexNetwork([None,None],directed=False,fullyInterconnected=True)
        mnet.add_layer("a",1)
        mnet.add_layer("b",1)
        mnet.add_layer("x",2)
        mnet.intranets["a","x"]=mono1
        self.assertEqual(sorted(mnet.intranets["a","x"].edges),sorted(mono1.edges))
        self.assertEqual(set(mnet.intranets["a","x"]),set([1,2,3]))
        
        mnet.intranets["b","x"]=mono2
        self.assertEqual(sorted(mnet.intranets["b","x"].edges),sorted(mono2.edges))
        self.assertEqual(set(mnet.intranets["b","x"]),set([1,2,3,4,5]))
        self.assertEqual(sorted(mnet.intranets["a","x"].edges),sorted(mono1.edges))
        self.assertEqual(set(mnet.intranets["a","x"]),set([1,2,3,4,5]))
        
    def test_selfedges(self):
        """Testing that self-edges work as expected.
        """

        #monoplex undirected
        mnet=net.MultilayerNetwork(aspects=0)
        mnet[1,1]=2
        mnet[1,2]=3
        mnet[3,3]=4

        self.assertEqual(mnet[1,1],2)
        self.assertEqual(mnet[1][1],2)
        self.assertEqual(mnet[2,2],mnet.noEdge)
        self.assertEqual(mnet[2][2],mnet.noEdge)
        self.assertEqual(mnet[3,3],4)
        self.assertEqual(mnet[3][3],4)


        self.assertEqual(mnet[1].deg(),2) #self-edges is only counted once in degree
        self.assertEqual(mnet[1].deg(),len(list(mnet[1])))
        self.assertEqual(mnet[3].deg(),1) #self-edges is only counted once in degree1
        self.assertEqual(mnet[3].deg(),len(list(mnet[3])))

        self.assertEqual(len(mnet.edges),len(list(mnet.edges))) #this should always be true
        self.assertEqual(len(list(mnet.edges)),3) #self-edges only once in the edge list


        #monoplex directed
        mnet=net.MultilayerNetwork(aspects=0,directed=True)
        mnet[1,1]=2
        mnet[1,1]=0
        mnet[1,1]=0
        mnet[1,2]=3
        mnet[3,3]=4
        mnet[1,1]=2

        self.assertEqual(mnet[1,1],2)
        self.assertEqual(mnet[1][1],2)
        self.assertEqual(mnet[2,2],mnet.noEdge)
        self.assertEqual(mnet[2][2],mnet.noEdge)
        self.assertEqual(mnet[3,3],4)
        self.assertEqual(mnet[3][3],4)


        self.assertEqual(mnet[1].deg(),2) #self-edges is only counted once in degree
        self.assertEqual(mnet[1].deg(),len(list(mnet[1])))
        self.assertEqual(mnet[3].deg(),1) #self-edges is only counted once in degree
        self.assertEqual(mnet[3].deg(),len(list(mnet[3])))

        self.assertEqual(len(mnet.edges),len(list(mnet.edges))) #this should always be true
        self.assertEqual(len(list(mnet.edges)),3) #self-edges only once in the edge list
        


def test_net():
    suite = unittest.TestSuite()    
    suite.addTest(TestNet("test_flat_mnet"))
    suite.addTest(TestNet("test_flat_directed_mnet"))
    suite.addTest(TestNet("test_flat_equal"))
    suite.addTest(TestNet("test_2dim_equal"))
    suite.addTest(TestNet("test_mplex_equal"))
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
    suite.addTest(TestNet("test_node_iterators_all"))
    suite.addTest(TestNet("test_mplex_intralayer_nets"))
    suite.addTest(TestNet("test_mlayer_2dim_nonglobalnodes"))
    suite.addTest(TestNet("test_mplex_adding_intralayer_nets"))
    suite.addTest(TestNet("test_selfedges"))
        
    return unittest.TextTestRunner().run(suite).wasSuccessful()


if __name__ == '__main__':
    sys.exit(not test_net())

