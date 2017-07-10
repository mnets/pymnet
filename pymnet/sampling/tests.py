# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import sys
import unittest
import time
from pymnet import net,models
import reqs
import dumb
import esu
import creators

class TestSampling(unittest.TestCase):
    
    def test_multilayer_partially_interconnected(self):
        nodelist = [[1,2,3],[2,3,4],[4,1,2]]
        net1 = creators.multilayer_partially_interconnected(nodelist,0)
        for nodelayer in list(net1.iter_node_layers()):
            self.assertEqual(net1[nodelayer[0],nodelayer[1]].deg(),0)
        net2 = creators.multilayer_partially_interconnected(nodelist,1)
        for nodelayer in list(net2.iter_node_layers()):
            self.assertEqual(net2[nodelayer[0],nodelayer[1]].deg(),8)

    def test_required_lengths(self):
        self.assertEqual((reqs.calculate_required_lengths([4,3,4,2],[3,2,2,1,2,1,1,2,1,1,1])),(6,4))
        self.assertEqual((reqs.calculate_required_lengths([1,2,1],[1,0,1,0])),(2,3))
        self.assertEqual((reqs.calculate_required_lengths([2,2,1],[1,0,1,0])),(3,3))
        self.assertEqual((reqs.calculate_required_lengths([1],[])),(1,1))
        self.assertEqual((reqs.calculate_required_lengths([9999],[])),(9999,1))
        self.assertNotEqual((reqs.calculate_required_lengths([5,3,4,2],[3,2,2,1,2,1,1,2,1,1,1])),(6,4))
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([49,999],[])
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([],[])
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([1],[1,2,3,4])
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([0,-1,1],[1,2,3,4])
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([0,0,0],[1,2,3,4])
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([0,0,0],[0,0,0,0])
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([1,1],[-1])
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([1,1],[0.5])
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([1,0.5],[1])
            
    def test_check_reqs(self):
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2[1,'X'][1,'Y'] = 1
        net2[1,'X'][2,'X'] = 1
        net3 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net3[1,'X'][1,'Y'] = 1
        net3[1,'X'][3,'X'] = 1
        net3[1,'Y'][1,'Z'] = 1
        net3[1,'Y'][2,'Z'] = 1
        net4 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net4[1,'X'][2,'X'] = 1
        net4[1,'X'][1,'Y'] = 1
        net4[1,'Y'][1,'Z'] = 1
        net4[1,'Z'][2,'Z'] = 1
        net5 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net5[1,'X'][2,'X'] = 1
        net5[1,'X'][1,'Y'] = 1
        net5[1,'Y'][1,'Z'] = 1
        net5[1,'Z'][2,'Z'] = 1
        net5[2,'Z'][2,'Y'] = 1
        net6 = models.full_multilayer(2,['X','Y','Z'])
        net7 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net7['X','X']['Z','X'] = 1
        net7['X','X']['X','Z'] = 1
        net7['X','Z']['Y','Z'] = 1
        net7['X','Z']['X','Y'] = 1
        net7['Y','Z']['Z','Z'] = 1
        net7['X','Y']['Z','Y'] = 1
        self.assertFalse(reqs.check_reqs(net1,[1],['X'],[1],[]))
        self.assertFalse(reqs.check_reqs(net1,[1],['X','Y'],[1,1],[1]))
        self.assertTrue(reqs.check_reqs(net2,[1],['X'],[1],[]))
        self.assertTrue(reqs.check_reqs(net2,[1,2],['X','Y'],[1,2],[1]))
        self.assertFalse(reqs.check_reqs(net2,[1,2],['X','Z'],[1,2],[1]))
        with self.assertRaises(AssertionError):
            reqs.check_reqs(net2,[1,2],['X','Y'],[1,2],[1,1])
        with self.assertRaises(AssertionError):
            reqs.check_reqs(net2,[1,2],['X'],[1,2],[1])
        with self.assertRaises(AssertionError):
            reqs.check_reqs(net2,[1],['X','Y'],[1,2],[1])
        with self.assertRaises(AssertionError):
            reqs.check_reqs(net2,[1,2],['X','Y'],[1,2],[1.5])
        self.assertTrue(reqs.check_reqs(net3,[1,3],['X','Y'],[1,2],[1]))
        self.assertTrue(reqs.check_reqs(net3,[2,1],['Y','Z'],[2,1],[1]))
        self.assertTrue(reqs.check_reqs(net3,[1,2,3],['Y','Z','X'],[2,2,1],[1,1,1,1]))
        self.assertFalse(reqs.check_reqs(net3,[1,2,3],['X','Z'],[2,2],[1]))
        with self.assertRaises(AssertionError):
            reqs.check_reqs(net3,[1,2,3],['X','Y'],[1,2],[1])
        self.assertFalse(reqs.check_reqs(net4,[1,2],['X','Y','Z'],[2,2,2],[2,2,2,2]))
        self.assertTrue(reqs.check_reqs(net5,[1,2],['X','Z','Y'],[2,2,2],[2,2,2,2]))
        with self.assertRaises(AssertionError):
            reqs.check_reqs(net5,[1,2],['X','Z','Y','Y'],[2,2,2],[2,2,2,2])
        self.assertTrue(reqs.check_reqs(net6,[1,0],['Y','Z','X'],[2,2,2],[2,2,2,2]))
        self.assertTrue(reqs.check_reqs(net6,[1,0],['Z','X'],[2,2],[2]))
        self.assertFalse(reqs.check_reqs(net6,[1,0],['Y','Z','X'],[2,1,2],[1,2,1,1]))
        self.assertTrue(reqs.check_reqs(net7,['X','Y'],['Z','Y','X'],[1,2,1],[1,1,1,1]))
        self.assertTrue(reqs.check_reqs(net7,['X','Y'],['X','Z'],[1,2],[1]))
        self.assertFalse(reqs.check_reqs(net7,['X','Z'],['X','Z'],[2,2],[2]))
    
    def test_dumb_enumeration(self):
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2[1,'X'][1,'Y'] = 1
        net2[1,'X'][2,'X'] = 1
        net3 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net3[1,'X'][1,'Y'] = 1
        net3[1,'X'][3,'X'] = 1
        net3[1,'Y'][1,'Z'] = 1
        net3[1,'Y'][2,'Z'] = 1
        net4 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net4[1,'X'][1,'Y'] = 1
        net4[1,'X'][2,'X'] = 1
        net5 = models.full_multilayer(2,['X','Y','Z'])
        net6 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net6[1,'X'][2,'X'] = 1
        net6[1,'X'][1,'Y'] = 1
        net6[1,'Y'][1,'Z'] = 1
        net6[1,'Z'][2,'Z'] = 1
        net6[2,'Z'][2,'Y'] = 1
        net7 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net7[1,'X'][2,'X'] = 1
        net7[1,'X'][1,'Y'] = 1
        net7[1,'Y'][1,'Z'] = 1
        net7[1,'Z'][2,'Z'] = 1
        net8 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net8[1,'X'][1,'Y'] = 1
        net8[1,'X'][2,'X'] = 1
        net8.add_node(2,layer='Y')
        resultlist = []
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[],[],resultlist)
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[2,1],[1,1],resultlist)
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[2,1],[],resultlist)
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[2,1,1],[1],resultlist)
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[],[1],resultlist)
        resultlist = []
        dumb.dumbEnumeration(net1,[1,2],[1],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net2,[1],[],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X']),([1],['Y']),([2],['X'])])
        resultlist = []
        dumb.dumbEnumeration(net2,[1,2],[1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        dumb.dumbEnumeration(net2,[2,1],[1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        dumb.dumbEnumeration(net3,[1,1],[1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y']),([1],['Y','Z'])])
        resultlist = []
        dumb.dumbEnumeration(net3,[2,1],[1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        dumb.dumbEnumeration(net3,[2,2],[1],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net3,[2,1,1],[1,0,0,0],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net3,[2,1,2],[1,1,1,1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumbEnumeration(net4,[1,2],[1],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net4,[2,2],[2],resultlist)
        self.assertEqual(resultlist,[])
        resultlist =  []
        dumb.dumbEnumeration(net5,[2,2,2],[2,2,2,2],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist =  []
        dumb.dumbEnumeration(net5,[2,2],[2],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0, 1], ['X', 'Y']), ([0, 1], ['X', 'Z']), ([0, 1], ['Y', 'Z'])])
        resultlist = []
        dumb.dumbEnumeration(net6,[2,2,2],[2,2,2,2],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        dumb.dumbEnumeration(net7,[2,2,2],[2,2,2,2],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net8,[1,2],[1],resultlist)
        self.assertEqual(resultlist,[])
        
    def test_esu_concise(self):
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2[1,'X'][1,'Y'] = 1
        net2[1,'X'][2,'X'] = 1
        net3 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net3[1,'X'][1,'Y'] = 1
        net3[1,'X'][3,'X'] = 1
        net3[1,'Y'][1,'Z'] = 1
        net3[1,'Y'][2,'Z'] = 1
        net4 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net4[1,'X'][1,'Y'] = 1
        net4[1,'X'][2,'X'] = 1
        net5 = models.full_multilayer(2,['X','Y','Z'])
        net6 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net6[1,'X'][2,'X'] = 1
        net6[1,'X'][1,'Y'] = 1
        net6[1,'Y'][1,'Z'] = 1
        net6[1,'Z'][2,'Z'] = 1
        net6[2,'Z'][2,'Y'] = 1
        net7 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net7[1,'X'][2,'X'] = 1
        net7[1,'X'][1,'Y'] = 1
        net7[1,'Y'][1,'Z'] = 1
        net7[1,'Z'][2,'Z'] = 1
        net8 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net8[1,'X'][1,'Y'] = 1
        net8[1,'X'][2,'X'] = 1
        net8.add_node(2,layer='Y')
        resultlist = []
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[],[],resultlist)
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[2,1],[1,1],resultlist)
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[2,1],[],resultlist)
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[2,1,1],[1],resultlist)
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,[],[1],resultlist)
        resultlist = []
        esu.enumerateSubgraphs(net1,[1,2],[1],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net2,[1],[],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X']),([1],['Y']),([2],['X'])])
        resultlist = []
        esu.enumerateSubgraphs(net2,[1,2],[1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        esu.enumerateSubgraphs(net2,[2,1],[1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        esu.enumerateSubgraphs(net3,[1,1],[1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y']),([1],['Y','Z'])])
        resultlist = []
        esu.enumerateSubgraphs(net3,[2,1],[1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        esu.enumerateSubgraphs(net3,[2,2],[1],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.enumerateSubgraphs(net3,[2,1,1],[1,0,0,0],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.enumerateSubgraphs(net3,[2,1,2],[1,1,1,1],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.enumerateSubgraphs(net4,[1,2],[1],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.enumerateSubgraphs(net4,[2,2],[2],resultlist)
        self.assertEqual(resultlist,[])
        resultlist =  []
        esu.enumerateSubgraphs(net5,[2,2,2],[2,2,2,2],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist =  []
        esu.enumerateSubgraphs(net5,[2,2],[2],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0, 1], ['X', 'Y']), ([0, 1], ['X', 'Z']), ([0, 1], ['Y', 'Z'])])
        resultlist = []
        esu.enumerateSubgraphs(net6,[2,2,2],[2,2,2,2],resultlist)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        esu.enumerateSubgraphs(net7,[2,2,2],[2,2,2,2],resultlist)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.enumerateSubgraphs(net8,[1,2],[1],resultlist)
        self.assertEqual(resultlist,[])
        
    def test_esu_exhaustive(self):
        # Will take approx. 45 min
        reqlist = [([1,1],[0]),([1,2],[0]),([1,2],[1]),([2,3],[1]),([2,1,1],[1,0,0,0])]
        for requirement in reqlist:
            for _ in range(30):
                network = creators.multilayer_partially_interconnected(creators.random_nodelists(30,10,5),0.05)
                resultlist_dumb = []
                resultlist_esu = []
                dumb.dumbEnumeration(network,requirement[0],requirement[1],resultlist_dumb)
                esu.enumerateSubgraphs(network,requirement[0],requirement[1],resultlist_esu)
                for result in resultlist_dumb:
                    result[0].sort()
                    result[1].sort()
                resultlist_dumb.sort()
                for result in resultlist_esu:
                    result[0].sort()
                    result[1].sort()
                resultlist_esu.sort()
                self.assertEqual(resultlist_dumb,resultlist_esu)
                
    def test_esu_insane(self):
        # Will run over weekend
        reqlist = [([1,1],[0]),([1,1],[1]),([1,2],[0]),([1,2],[1]),([1,3],[0]),([1,3],[1]),([2,3],[0]),([2,3],[1]),([2,3],[2]),([3,3],[0]),([3,3],[1]),([3,3],[2]),([3,3],[3])]    
        reqlist = reqlist + [([1,1,1],[0,0,0,0]),([1,1,1],[1,0,0,0]),([1,1,1],[1,1,1,1])]
        reqlist = reqlist + [([2,1,1],[0,0,0,0]),([2,1,1],[1,0,0,0]),([2,1,1],[1,1,1,1])]
        reqlist = reqlist + [([2,2,1],[0,0,0,0]),([2,2,1],[1,0,0,0]),([2,2,1],[2,0,0,0]),([2,2,1],[1,1,0,0]),([2,2,1],[1,0,1,0]),([2,2,1],[1,1,1,1]),([2,2,1],[2,0,0,0]),([2,2,1],[2,1,1,1])]
        for requirement in reqlist:
            for _ in range(100):
                network = creators.multilayer_partially_interconnected(creators.random_nodelists(30,10,5),0.05)
                resultlist_dumb = []
                resultlist_esu = []
                dumb.dumbEnumeration(network,requirement[0],requirement[1],resultlist_dumb)
                esu.enumerateSubgraphs(network,requirement[0],requirement[1],resultlist_esu)
                for result in resultlist_dumb:
                    result[0].sort()
                    result[1].sort()
                resultlist_dumb.sort()
                for result in resultlist_esu:
                    result[0].sort()
                    result[1].sort()
                resultlist_esu.sort()
                self.assertEqual(resultlist_dumb,resultlist_esu)
                
    def test_esu_performance(self):
        reqlist = [([1,1],[0]),([1,1],[1]),([1,2],[0]),([1,2],[1]),([1,3],[0]),([1,3],[1]),([2,3],[0]),([2,3],[1]),([2,3],[2]),([3,3],[0]),([3,3],[1]),([3,3],[2]),([3,3],[3])]    
        reqlist = reqlist + [([1,1,1],[0,0,0,0]),([1,1,1],[1,0,0,0]),([1,1,1],[1,1,1,1])]
        reqlist = reqlist + [([2,1,1],[0,0,0,0]),([2,1,1],[1,0,0,0]),([2,1,1],[1,1,1,1])]
        reqlist = reqlist + [([2,2,1],[0,0,0,0]),([2,2,1],[1,0,0,0]),([2,2,1],[2,0,0,0]),([2,2,1],[1,1,0,0]),([2,2,1],[1,0,1,0]),([2,2,1],[1,1,1,1]),([2,2,1],[2,0,0,0]),([2,2,1],[2,1,1,1])]
        network = creators.multilayer_partially_interconnected(creators.random_nodelists(30,10,5,seed=231),0.07,seed=1)
        network[30,2][31,2]=1
        network[31,2][31,3]=1
        network[31,3][30,3]=1
        network[30,3][31,4]=1
        start = time.time()        
        for requirement in reqlist:
            resultlist_esu = []
            esu.enumerateSubgraphs(network,requirement[0],requirement[1],resultlist_esu)
        print("Time taken "+str(time.time()-start)+" s")
        
def makesuite(exhaustive=False,insane=False,performance=False):
    suite = unittest.TestSuite()
    suite.addTest(TestSampling("test_multilayer_partially_interconnected"))
    suite.addTest(TestSampling("test_required_lengths"))
    suite.addTest(TestSampling("test_check_reqs"))
    suite.addTest(TestSampling("test_dumb_enumeration"))
    suite.addTest(TestSampling("test_esu_concise"))
    if exhaustive:
        suite.addTest(TestSampling("test_esu_exhaustive"))
    if insane:
        suite.addTest(TestSampling("test_esu_insane"))
    if performance:
        suite.addTest(TestSampling("test_esu_performance"))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(makesuite(exhaustive=False,insane=False,performance=True))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    