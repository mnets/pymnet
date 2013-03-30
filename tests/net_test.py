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

                
    def test_simple_couplings_mnet(self):
        testnet=net.MultisliceNetwork()
        testnet[1,1,'a','b']=1
        testnet[2,2,'a','b']=1
        testnet[3,3,'a','b']=1
        self.test_simple_couplings(testnet)

def test_net():
    suite = unittest.TestSuite()    
    #symmetric tests:
    suite.addTest(TestNet("test_simple_couplings_mnet"))

    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_net()

