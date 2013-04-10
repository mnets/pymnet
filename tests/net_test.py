import unittest
from operator import itemgetter

import sys
sys.path.append("../../")
from pymnet import net
#from .. import net


class TestNet(unittest.TestCase):
    
    def setUp(self):
        pass

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


    def test_flat_mnet(self):
        testnet=net.MultisliceNetwork(dimensions=1)
        self.test_flat(testnet)


    def test_simple_couplings(self,net):
        """Tests basic functionality of Multiplex networks with two layers.

        The input network must have connections between nodes i,i,s,s, where
        i is in {1,2,3} and s is in {'a','b'}.
        """
        #First, we add some links
        net[1,2,'a']=1
        net[2,3,'a']=1
        net[1,2,'b']=1
        net[1,3,'b']=1

        #Test the lattice
        self.assertEqual(net[1,1,'a','b'],1)
        self.assertEqual(net[1,1,'b','a'],1)
        self.assertEqual(net[1,2,'a','b'],0)

        #Tests for network structure
        self.assertEqual(net[1,2,'a','a'],1)
        self.assertEqual(net[2,1,'a','a'],1)
        self.assertEqual(net[2,3,'a','a'],1)
        self.assertEqual(net[3,2,'a','a'],1)
        self.assertEqual(net[1,2,'b','b'],1)
        self.assertEqual(net[2,1,'b','b'],1)
        self.assertEqual(net[1,3,'b','b'],1)
        self.assertEqual(net[3,1,'b','b'],1)

        #TODO: Tests for missing links, inside and outside network

        #TODO: Tests for alternative notations

        #Tests for node iterators
        self.assertEqual(set(net[1,'a']),set([(1,'b'),(2,'a')]))
        self.assertEqual(set(net[1,:,'a',:]),set([(1,'b'),(2,'a')]))
        self.assertEqual(list(net[1,:,'a','a']),[(2,'a')])
        self.assertEqual(list(net[1,1,'a',:]),[(1,'b')])

        #TODO: Tests for degrees and strength

        #TODO: Tests for iterating over nodes and layers

    #TODO: Add tests for removing links by setting them to 0
                
    def test_simple_couplings_mnet(self):
        testnet=net.MultisliceNetwork(dimensions=2)
        testnet[1,1,'a','b']=1
        testnet[2,2,'a','b']=1
        testnet[3,3,'a','b']=1
        self.test_simple_couplings(testnet)


    def test_simple_couplings_cmnet(self):
        testnet=net.CoupledMultiplexNetwork(couplings=[('categorical',1.0)])
        self.test_simple_couplings(testnet)


    def test_2dim_categorical_couplings(self,net):
        net[1,2,'a','x']=1
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

        self.assertEqual(net[1,2,'a','a','x','x'],1)
        self.assertEqual(net[1,1,'a','b','x','x'],1)
        self.assertEqual(net[1,1,'a','a','x','y'],1)
        
        self.assertEqual(net[1,2,'a','b','x','x'],0)
        self.assertEqual(net[1,2,'a','b','x','y'],0)
        self.assertEqual(net[1,1,'a','b','x','y'],0)

    def test_2dim_categorical_couplings_mnet(self): 
        testnet=net.MultisliceNetwork(dimensions=3)
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
        self.test_2dim_categorical_couplings(testnet)

    def test_2dim_categorical_couplings_cmnet(self):
        testnet=net.CoupledMultiplexNetwork(couplings=[('categorical',1.0),('categorical',1.0)])
        self.test_2dim_categorical_couplings(testnet)

def test_net():
    suite = unittest.TestSuite()    
    suite.addTest(TestNet("test_flat_mnet"))
    suite.addTest(TestNet("test_simple_couplings_mnet"))
    suite.addTest(TestNet("test_simple_couplings_cmnet"))
    suite.addTest(TestNet("test_2dim_categorical_couplings_mnet"))
    suite.addTest(TestNet("test_2dim_categorical_couplings_cmnet"))

    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_net()

