import unittest
from operator import itemgetter

import sys
sys.path.append("../../")
from pymnet import net
#from .. import net


class TestNet(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_simple_couplings(self,net):
        net[1,2,'a']=1
        net[2,3,'a']=1
        net[1,2,'b']=1
        net[1,3,'b']=1

        self.assertEqual(net[1,2,'a','a'],1)

        self.assertEqual(set(net[1,'a']),set([(1,'b'),(2,'a')]))
        self.assertEqual(set(net[1,:,'a',:]),set([(1,'b'),(2,'a')]))
        self.assertEqual(list(net[1,:,'a','a']),[(2,'a')])
        self.assertEqual(list(net[1,1,'a',:]),[(1,'b')])
                
    def test_simple_couplings_mnet(self):
        testnet=net.MultisliceNetwork(dimensions=2)
        testnet[1,1,'a','b']=1
        testnet[2,2,'a','b']=1
        testnet[3,3,'a','b']=1
        self.test_simple_couplings(testnet)


    def test_simple_couplings_cmnet(self):
        testnet=net.CoupledMultiplexNetwork(couplings=[('categorical',1.0)])
        self.test_simple_couplings(testnet)

def test_net():
    suite = unittest.TestSuite()    
    #symmetric tests:
    suite.addTest(TestNet("test_simple_couplings_mnet"))
    suite.addTest(TestNet("test_simple_couplings_cmnet"))

    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_net()

