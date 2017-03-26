import unittest
from operator import itemgetter
import math
import sys

from pymnet import net,models,diagnostics



class TestModels(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_monoplex_erdosrenyi(self):
        size=10
        full=net.MultilayerNetwork(aspects=0)
        models.single_layer_er(full,range(10,10+size),p=None,edges=int((size*(size-1))/2))
        for i in full:
            for j in full:
                if i!=j:
                    self.assertEqual(full[i,j],1)
        self.assertEqual(len(full.edges),int((size*(size-1))/2))

        net2=net.MultilayerNetwork(aspects=0)
        models.single_layer_er(net2,range(10),p=None,edges=30)
        self.assertEqual(len(net2.edges),30)

    def test_multiplex_erdosrenyi(self):
        net=models.er(10,0.5)
        net2=models.er(10,[0.4,0.6])

        #test that there are some links but not all
        self.assertTrue(1<len(list(net.edges))<10*9/2.)
        self.assertTrue(1<len(list(net2.A[1].edges))<10*9+10)

        net3=models.er(10,edges=[30,45])
        self.assertEqual(len(net3.A[0].edges),30)
        self.assertEqual(len(net3.A[1].edges),45)

        net4=models.er([range(10),range(5,15)],edges=[30,45])
        self.assertEqual(len(net4.A[0].edges),30)
        self.assertEqual(len(net4.A[1].edges),45)
        self.assertEqual(set(net4.A[0]),set(range(10)))
        self.assertEqual(set(net4.A[1]),set(range(5,15)))

        net5=models.er([range(10),range(5,15)],edges=30)
        self.assertEqual(len(net5.A[0].edges),30)
        self.assertEqual(len(net5.A[1].edges),30)
        self.assertEqual(set(net5.A[0]),set(range(10)))
        self.assertEqual(set(net5.A[1]),set(range(5,15)))


    def test_monoplex_configuration_model(self):
        net=models.conf({5:1000}) #maxdeg << sqrt(number of nodes)
        self.assertEqual(diagnostics.degs(net),{5:1000})

        net=models.conf({50:100})
        self.assertEqual(diagnostics.degs(net),{50:100})

        #zero degrees
        net=models.conf({50:100,0:10})
        self.assertEqual(diagnostics.degs(net),{50:100,0:10})

        net=models.conf(dict(map(lambda x:(x,int(math.sqrt(x)+1)),range(101))),degstype="nodes")
        for i in range(101):
            self.assertEqual(net[i].deg(),int(math.sqrt(i)+1))

        #zero degrees
        net=models.conf(dict(map(lambda x:(x,int(math.sqrt(x))),range(99))),degstype="nodes")
        for i in range(99):
            self.assertEqual(net[i].deg(),int(math.sqrt(i)))

        net=models.conf(net)
        for i in range(99):
            self.assertEqual(net[i].deg(),int(math.sqrt(i)))

    def test_multiplex_configuration_model(self):
        net=models.conf([{50:100},{50:100}])
        self.assertEqual(diagnostics.multiplex_degs(net),{0:{50:100},1:{50:100}})

        net=models.conf({"l1":{50:100},"l2":{50:100}})
        self.assertEqual(diagnostics.multiplex_degs(net),{"l1":{50:100},"l2":{50:100}})

        net=models.conf(net)
        self.assertEqual(diagnostics.multiplex_degs(net),{"l1":{50:100},"l2":{50:100}})

        degs={"l1":dict(map(lambda x:(x,2*int(math.sqrt(x))),range(100))),"l2":dict(map(lambda x:(x,2*int(math.sqrt(x))),range(20,120)))}
        net=models.conf(degs,degstype="nodes")
        self.assertEqual(diagnostics.multiplex_degs(net,degstype="nodes"),degs)
        self.assertEqual(set(net.A["l1"]),set(range(100)))
        self.assertEqual(set(net.A["l2"]),set(range(20,120)))

def test_models():
    suite = unittest.TestSuite()    
    suite.addTest(TestModels("test_monoplex_erdosrenyi"))
    suite.addTest(TestModels("test_multiplex_erdosrenyi"))
    suite.addTest(TestModels("test_monoplex_configuration_model"))
    suite.addTest(TestModels("test_multiplex_configuration_model"))

    return unittest.TextTestRunner().run(suite).wasSuccessful() 

if __name__ == '__main__':
    sys.exit(not test_models())

