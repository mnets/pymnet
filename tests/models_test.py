import unittest
from operator import itemgetter

import sys
sys.path.append("../../")
from pymnet import net,models
#from .. import net


class TestNet(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_multiplex_erdosrenyi(self):
        net=models.er(10,0.5)
        net2=models.er(10,[0.4,0.6])

        #test that there are some links but not all
        self.assertTrue(1<len(list(net.edges))<10*9/2.)
        self.assertTrue(1<len(list(net2.A[1].edges))<10*9+10)

def test_net():
    suite = unittest.TestSuite()    
    suite.addTest(TestNet("test_multiplex_erdosrenyi"))

    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_net()

