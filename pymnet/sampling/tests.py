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
            for _ in range(10):
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
                
    def test_esu_performance(self):
        reqlist = [([1,1],[0]),([1,1],[1]),([1,2],[0]),([1,2],[1]),([1,3],[0]),([1,3],[1]),([2,3],[0]),([2,3],[1]),([2,3],[2]),([3,3],[0]),([3,3],[1]),([3,3],[2]),([3,3],[3])]    
        reqlist = reqlist + [([1,1,1],[0,0,0,0]),([1,1,1],[1,0,0,0]),([1,1,1],[1,1,1,1])]
        reqlist = reqlist + [([2,1,1],[0,0,0,0]),([2,1,1],[1,0,0,0]),([2,1,1],[1,1,1,1])]
        reqlist = reqlist + [([2,2,1],[0,0,0,0]),([2,2,1],[1,0,0,0]),([2,2,1],[2,0,0,0]),([2,2,1],[1,1,0,0]),([2,2,1],[1,0,1,0]),([2,2,1],[1,1,1,1]),([2,2,1],[2,0,0,0]),([2,2,1],[2,1,1,1])]
        #network = creators.multilayer_partially_interconnected(creators.random_nodelists(30,10,5,seed=231),0.08,seed=1)
        #network[30,2][31,2]=1
        #network[31,2][31,3]=1
        #network[31,3][30,3]=1
        #network[30,3][31,4]=1
        network = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        nodelayerlist = [(5, 0),(11, 0),(17, 0),(18, 0),(22, 0),
                        (23, 0),(25, 0),(27, 0),(28, 0),(29, 0),
                        (2, 1),(7, 1),(9, 1),(13, 1),(15, 1),
                        (18, 1),(19, 1),(22, 1),(25, 1),(29, 1),
                        (0, 2),(1, 2),(7, 2),(9, 2),(10, 2),
                        (15, 2),(20, 2),(22, 2),(25, 2),(26, 2),
                        (30, 2),(31, 2),(1, 3),(2, 3),(5, 3),
                        (8, 3),(14, 3),(17, 3),(19, 3),(20, 3),
                        (23, 3),(29, 3),(30, 3),(31, 3),(0, 4),
                        (1, 4),(7, 4),(8, 4),(14, 4),(15, 4),
                        (16, 4),(18, 4),(24, 4),(29, 4),(31, 4)]
        edgelist = [(0, 25, 2, 2, 1),(0, 22, 2, 0, 1),(0, 2, 2, 1, 1),(0, 14, 4, 4, 1),(0, 2, 4, 1, 1),(0, 15, 4, 1, 1),(1, 1, 2, 4, 1),
                    (1, 24, 2, 4, 1),(1, 22, 3, 2, 1),(1, 20, 3, 3, 1),(1, 7, 3, 1, 1),(1, 25, 3, 0, 1),(1, 17, 3, 3, 1),(1, 23, 3, 0, 1),
                    (1, 10, 3, 2, 1),(1, 17, 4, 3, 1),(1, 26, 4, 2, 1),(1, 19, 4, 3, 1),(1, 29, 4, 3, 1),(2, 22, 1, 2, 1),(2, 14, 1, 4, 1),
                    (2, 24, 1, 4, 1),(2, 19, 1, 3, 1),(2, 18, 1, 1, 1),(2, 29, 3, 1, 1),(5, 10, 0, 2, 1),(5, 28, 0, 0, 1),(5, 17, 0, 3, 1),
                    (5, 18, 0, 4, 1),(5, 15, 0, 1, 1),(5, 20, 3, 2, 1),(5, 17, 3, 0, 1),(5, 23, 3, 0, 1),(5, 22, 3, 0, 1),(7, 25, 1, 0, 1),
                    (7, 26, 1, 2, 1),(7, 20, 1, 3, 1),(7, 8, 1, 4, 1),(7, 28, 2, 0, 1),(7, 19, 2, 1, 1),(7, 25, 2, 1, 1),(7, 29, 2, 0, 1),
                    (7, 16, 2, 4, 1),(7, 8, 4, 3, 1),(7, 29, 4, 4, 1),(7, 25, 4, 1, 1),(7, 15, 4, 1, 1),(8, 29, 3, 0, 1),(8, 25, 3, 0, 1),
                    (8, 14, 3, 3, 1),(8, 8, 3, 4, 1),(8, 10, 3, 2, 1),(8, 18, 4, 4, 1),(8, 9, 4, 1, 1),(8, 29, 4, 4, 1),(9, 29, 1, 4, 1),
                    (9, 19, 1, 3, 1),(9, 18, 1, 1, 1),(9, 29, 1, 0, 1),(9, 29, 2, 1, 1),(9, 29, 2, 4, 1),(9, 29, 2, 3, 1),(10, 23, 2, 0, 1),
                    (11, 29, 0, 1, 1),(13, 24, 1, 4, 1),(14, 18, 3, 0, 1),(14, 17, 3, 3, 1),(14, 22, 3, 2, 1),(14, 23, 4, 3, 1),(15, 27, 4, 0, 1),
                    (15, 17, 4, 0, 1),(16, 25, 4, 2, 1),(16, 23, 4, 0, 1),(16, 25, 4, 1, 1),(16, 26, 4, 2, 1),(17, 29, 3, 1, 1),(18, 25, 0, 0, 1),
                    (18, 18, 0, 4, 1),(18, 26, 1, 2, 1),(18, 24, 1, 4, 1),(18, 26, 4, 2, 1),(18, 23, 4, 3, 1),(18, 23, 4, 0, 1),(18, 22, 4, 1, 1),
                    (19, 29, 1, 1, 1),(20, 27, 2, 0, 1),(20, 29, 2, 3, 1),(20, 27, 3, 0, 1),(22, 24, 0, 4, 1),(22, 29, 0, 0, 1),(22, 29, 0, 3, 1),
                    (22, 25, 2, 2, 1),(23, 26, 3, 2, 1),(25, 26, 1, 2, 1),(25, 25, 1, 2, 1),(25, 29, 1, 4, 1),(25, 26, 2, 2, 1),(27, 29, 0, 0, 1),
                    (30, 31, 2, 2, 1),(30, 31, 3, 4, 1),(30, 31, 3, 3, 1),(31, 31, 2, 3, 1)]
        for nodelayer in nodelayerlist:
            network.add_node(node=nodelayer[0],layer=nodelayer[1])
        for edge in edgelist:
            network[edge[0],edge[1],edge[2],edge[3]] = 1
        start = time.time()
        for _ in range(1):
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    