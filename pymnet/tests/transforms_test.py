import unittest
from operator import itemgetter

import sys
sys.path.append("../../")
from pymnet import net,transforms



class TestNet(unittest.TestCase):
    
    def setUp(self):
        pass


    def test_aggregate_unweighted_mplex_simple(self):
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

        an=transforms.aggregate(n,1)
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

def test_net():
    suite = unittest.TestSuite()    
    suite.addTest(TestNet("test_aggregate_unweighted_mplex_simple"))
    suite.addTest(TestNet("test_aggregate_2dim_mplex"))

    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_net()

