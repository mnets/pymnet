# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import sys
import unittest
import time
import scipy,scipy.stats
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

    def test_default_required_lengths(self):
        self.assertEqual((reqs.default_calculate_required_lengths(sizes=[4,3,4,2],intersections=[3,2,2,1,2,1,1,2,1,1,1])),(6,4))
        self.assertEqual((reqs.default_calculate_required_lengths(sizes=[1,2,1],intersections=[1,0,1,0])),(2,3))
        self.assertEqual((reqs.default_calculate_required_lengths(sizes=[2,2,1],intersections=[1,0,1,0])),(3,3))
        self.assertEqual((reqs.default_calculate_required_lengths(sizes=[1],intersections=[])),(1,1))
        self.assertEqual((reqs.default_calculate_required_lengths(sizes=[9999],intersections=[])),(9999,1))
        self.assertNotEqual((reqs.default_calculate_required_lengths(sizes=[5,3,4,2],intersections=[3,2,2,1,2,1,1,2,1,1,1])),(6,4))
        with self.assertRaises(AssertionError):
            reqs.default_calculate_required_lengths(sizes=[49,999],intersections=[])
        with self.assertRaises(AssertionError):
            reqs.default_calculate_required_lengths(sizes=[],intersections=[])
        with self.assertRaises(AssertionError):
            reqs.default_calculate_required_lengths(sizes=[1],intersections=[1,2,3,4])
        with self.assertRaises(AssertionError):
            reqs.default_calculate_required_lengths(sizes=[0,-1,1],intersections=[1,2,3,4])
        with self.assertRaises(AssertionError):
            reqs.default_calculate_required_lengths(sizes=[0,0,0],intersections=[1,2,3,4])
        with self.assertRaises(AssertionError):
            reqs.default_calculate_required_lengths(sizes=[0,0,0],intersections=[0,0,0,0])
        with self.assertRaises(AssertionError):
            reqs.default_calculate_required_lengths(sizes=[1,1],intersections=[-1])
        with self.assertRaises(AssertionError):
            reqs.default_calculate_required_lengths(sizes=[1,1],intersections=[0.5])
        with self.assertRaises(AssertionError):
            reqs.default_calculate_required_lengths(sizes=[1,0.5],intersections=[1])
            
    def test_default_check_reqs(self):
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
        self.assertFalse(reqs.default_check_reqs(net1,[1],['X'],sizes=[1],intersections=[]))
        self.assertFalse(reqs.default_check_reqs(net1,[1],['X','Y'],sizes=[1,1],intersections=[1]))
        self.assertTrue(reqs.default_check_reqs(net2,[1],['X'],sizes=[1],intersections=[]))
        self.assertTrue(reqs.default_check_reqs(net2,[1,2],['X','Y'],sizes=[1,2],intersections=[1]))
        self.assertFalse(reqs.default_check_reqs(net2,[1,2],['X','Z'],sizes=[1,2],intersections=[1]))
        with self.assertRaises(AssertionError):
            reqs.default_check_reqs(net2,[1,2],['X','Y'],sizes=[1,2],intersections=[1,1])
        with self.assertRaises(AssertionError):
            reqs.default_check_reqs(net2,[1,2],['X'],sizes=[1,2],intersections=[1])
        with self.assertRaises(AssertionError):
            reqs.default_check_reqs(net2,[1],['X','Y'],sizes=[1,2],intersections=[1])
        with self.assertRaises(AssertionError):
            reqs.default_check_reqs(net2,[1,2],['X','Y'],sizes=[1,2],intersections=[1.5])
        self.assertTrue(reqs.default_check_reqs(net3,[1,3],['X','Y'],sizes=[1,2],intersections=[1]))
        self.assertTrue(reqs.default_check_reqs(net3,[2,1],['Y','Z'],sizes=[2,1],intersections=[1]))
        self.assertTrue(reqs.default_check_reqs(net3,[1,2,3],['Y','Z','X'],sizes=[2,2,1],intersections=[1,1,1,1]))
        self.assertFalse(reqs.default_check_reqs(net3,[1,2,3],['X','Z'],sizes=[2,2],intersections=[1]))
        with self.assertRaises(AssertionError):
            reqs.default_check_reqs(net3,[1,2,3],['X','Y'],sizes=[1,2],intersections=[1])
        self.assertFalse(reqs.default_check_reqs(net4,[1,2],['X','Y','Z'],sizes=[2,2,2],intersections=[2,2,2,2]))
        self.assertTrue(reqs.default_check_reqs(net5,[1,2],['X','Z','Y'],sizes=[2,2,2],intersections=[2,2,2,2]))
        with self.assertRaises(AssertionError):
            reqs.default_check_reqs(net5,[1,2],['X','Z','Y','Y'],sizes=[2,2,2],intersections=[2,2,2,2])
        self.assertTrue(reqs.default_check_reqs(net6,[1,0],['Y','Z','X'],sizes=[2,2,2],intersections=[2,2,2,2]))
        self.assertTrue(reqs.default_check_reqs(net6,[1,0],['Z','X'],sizes=[2,2],intersections=[2]))
        self.assertFalse(reqs.default_check_reqs(net6,[1,0],['Y','Z','X'],sizes=[2,1,2],intersections=[1,2,1,1]))
        self.assertTrue(reqs.default_check_reqs(net7,['X','Y'],['Z','Y','X'],sizes=[1,2,1],intersections=[1,1,1,1]))
        self.assertTrue(reqs.default_check_reqs(net7,['X','Y'],['X','Z'],sizes=[1,2],intersections=[1]))
        self.assertFalse(reqs.default_check_reqs(net7,['X','Z'],['X','Z'],sizes=[2,2],intersections=[2]))
    
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
            dumb.dumbEnumeration(net2,resultlist,sizes=[],intersections=[])
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,resultlist,sizes=[2,1],intersections=[1,1])
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,resultlist,sizes=[2,1],intersections=[])
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,resultlist,sizes=[2,1,1],intersections=[1])
        with self.assertRaises(AssertionError):
            dumb.dumbEnumeration(net2,resultlist,sizes=[],intersections=[1])
        resultlist = []
        dumb.dumbEnumeration(net1,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net2,resultlist,sizes=[1],intersections=[])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X']),([1],['Y']),([2],['X'])])
        resultlist = []
        dumb.dumbEnumeration(net2,resultlist,sizes=[1,2],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        dumb.dumbEnumeration(net2,resultlist,sizes=[2,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        dumb.dumbEnumeration(net3,resultlist,sizes=[1,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y']),([1],['Y','Z'])])
        resultlist = []
        dumb.dumbEnumeration(net3,resultlist,sizes=[2,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        dumb.dumbEnumeration(net3,resultlist,sizes=[2,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net3,resultlist,sizes=[2,1,1],intersections=[1,0,0,0])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net3,resultlist,sizes=[2,1,2],intersections=[1,1,1,1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumbEnumeration(net4,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net4,resultlist,sizes=[2,2],intersections=[2])
        self.assertEqual(resultlist,[])
        resultlist =  []
        dumb.dumbEnumeration(net5,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist =  []
        dumb.dumbEnumeration(net5,resultlist,sizes=[2,2],intersections=[2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0, 1], ['X', 'Y']), ([0, 1], ['X', 'Z']), ([0, 1], ['Y', 'Z'])])
        resultlist = []
        dumb.dumbEnumeration(net6,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        dumb.dumbEnumeration(net7,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumbEnumeration(net8,resultlist,sizes=[1,2],intersections=[1])
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
            esu.enumerateSubgraphs(net2,resultlist,sizes=[],intersections=[])
        with self.assertRaises(AssertionError):
            esu.enumerateSubgraphs(net2,resultlist,sizes=[2,1],intersections=[1,1])
        with self.assertRaises(AssertionError):
            esu.enumerateSubgraphs(net2,resultlist,sizes=[2,1],intersections=[])
        with self.assertRaises(AssertionError):
            esu.enumerateSubgraphs(net2,resultlist,sizes=[2,1,1],intersections=[1])
        with self.assertRaises(AssertionError):
            esu.enumerateSubgraphs(net2,resultlist,sizes=[],intersections=[1])
        resultlist = []
        esu.enumerateSubgraphs(net1,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.enumerateSubgraphs(net2,resultlist,sizes=[1],intersections=[])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X']),([1],['Y']),([2],['X'])])
        resultlist = []
        esu.enumerateSubgraphs(net2,resultlist,sizes=[1,2],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        esu.enumerateSubgraphs(net2,resultlist,sizes=[2,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        esu.enumerateSubgraphs(net3,resultlist,sizes=[1,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y']),([1],['Y','Z'])])
        resultlist = []
        esu.enumerateSubgraphs(net3,resultlist,sizes=[2,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        esu.enumerateSubgraphs(net3,resultlist,sizes=[2,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.enumerateSubgraphs(net3,resultlist,sizes=[2,1,1],intersections=[1,0,0,0])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.enumerateSubgraphs(net3,resultlist,sizes=[2,1,2],intersections=[1,1,1,1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.enumerateSubgraphs(net4,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.enumerateSubgraphs(net4,resultlist,sizes=[2,2],intersections=[2])
        self.assertEqual(resultlist,[])
        resultlist =  []
        esu.enumerateSubgraphs(net5,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist =  []
        esu.enumerateSubgraphs(net5,resultlist,sizes=[2,2],intersections=[2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0, 1], ['X', 'Y']), ([0, 1], ['X', 'Z']), ([0, 1], ['Y', 'Z'])])
        resultlist = []
        esu.enumerateSubgraphs(net6,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        esu.enumerateSubgraphs(net7,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.enumerateSubgraphs(net8,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        
    def test_esu_exhaustive(self):
        reqlist = [([1,1],[0]),([1,2],[0]),([1,2],[1]),([2,3],[1]),([2,1,1],[1,0,0,0])]
        for requirement in reqlist:
            for _ in range(1):
                network = creators.multilayer_partially_interconnected(creators.random_nodelists(30,10,5),0.05)
                resultlist_dumb = []
                resultlist_esu = []
                dumb.dumbEnumeration(network,resultlist_dumb,sizes=requirement[0],intersections=requirement[1])
                esu.enumerateSubgraphs(network,resultlist_esu,sizes=requirement[0],intersections=requirement[1])
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
        # PyPy recommended for speed
        reqlist = [([1,1],[0]),([1,1],[1]),([1,2],[0]),([1,2],[1]),([1,3],[0]),([1,3],[1]),([2,3],[0]),([2,3],[1]),([2,3],[2]),([3,3],[0]),([3,3],[1]),([3,3],[2]),([3,3],[3])]    
        reqlist = reqlist + [([1,1,1],[0,0,0,0]),([1,1,1],[1,0,0,0]),([1,1,1],[1,1,1,1])]
        reqlist = reqlist + [([2,1,1],[0,0,0,0]),([2,1,1],[1,0,0,0]),([2,1,1],[1,1,1,1])]
        reqlist = reqlist + [([2,2,1],[0,0,0,0]),([2,2,1],[1,0,0,0]),([2,2,1],[2,0,0,0]),([2,2,1],[1,1,0,0]),([2,2,1],[1,0,1,0]),([2,2,1],[1,1,1,1]),([2,2,1],[2,0,0,0]),([2,2,1],[2,1,1,1])]
        for requirement in reqlist:
            for _ in range(1):
                network = creators.multilayer_partially_interconnected(creators.random_nodelists(30,10,5),0.05)
                resultlist_dumb = []
                resultlist_esu = []
                dumb.dumbEnumeration(network,resultlist_dumb,sizes=requirement[0],intersections=requirement[1])
                esu.enumerateSubgraphs(network,resultlist_esu,sizes=requirement[0],intersections=requirement[1])
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
                esu.enumerateSubgraphs(network,resultlist_esu,sizes=requirement[0],intersections=requirement[1])
        print("Time taken "+str(time.time()-start)+" s")
        
    def _statistical_sample(self,network,iterations,motif,p,all_subgraphs):
        samplings = dict()
        for subgraph in all_subgraphs:
            subgraph[0].sort()
            subgraph[1].sort()
            samplings[tuple((tuple(subgraph[0]),tuple(subgraph[1])))] = []
        start = time.time()
        for _ in range(iterations):
            resultlist = []
            esu.enumerateSubgraphs(network,motif[0],motif[1],resultlist,p)
            for result in resultlist:
                result[0].sort()
                result[1].sort()
            resultlist = [tuple((tuple(result[0]),tuple(result[1]))) for result in resultlist]
            resultlist = set(resultlist)
            for entry in samplings:
                if entry in resultlist:
                    samplings[entry].append(1)
                else:
                    samplings[entry].append(0)
        print("Iterated in: "+str(time.time()-start)+" s")
        return samplings
        
    def test_esu_distribution_width(self,network=None,threshold=0.001,iterations=10000,motif=([2,1],[1]),splitlen=200,p=None,all_subgraphs=None):
        """
        A crude test for checking that the width of the sampling distribution corresponds to the 
        width of the binomial distribution from which the samples should originate. Does a repeated
        sampling of a network and calculates Pr for each instance of a motif in a network:
        
        Pr = the probability that, assuming that the sample is from the corresponding binomial distribution,
        there is at least one value in the sample at least as far away from the expected value as the farthest value
        found in the sample.
        
        This is a crude measure of sampling distribution width relative to the width of the binomial distribution
        that the algorithm should be sampling from if everything is correct. If the algorithm samples a distribution wider
        than the binomial distribution, Pr will be small.
        The check is done for each instance of a motif found in the network specified in the code. The actual default network
        may vary between different compilers/interpreters. Since no multiple correction is used and since crossing the
        threshold doesn't automatically mean that the algorithm isn't working correctly, the test is passed whether
        the threshold is crossed or not. If there are multiple Pr's smaller than a reasonable threshold, this might
        indicate that something is wrong with the algorithm.
        PyPy recommended for speed.
        """
        # TODO: Multiple correction and single value reporting
        if network == None:
            network = creators.multilayer_partially_interconnected(creators.random_nodelists(100,30,10,seed=1),0.05,seed=1)       
        if p == None:
            req_nodelist_len,req_layerlist_len = reqs.default_calculate_required_lengths(motif[0],motif[1])
            p = [0.5] * (req_nodelist_len-1 + req_layerlist_len-1 + 1)
        if all_subgraphs == None:
            all_subgraphs = []
            esu.enumerateSubgraphs(network,motif[0],motif[1],all_subgraphs)
        data = self._statistical_sample(network,iterations,motif,p,all_subgraphs)
        outlier_count = 0
        for motif in data:
            splitdata = [sum(split) for split in [data[motif][i:i+splitlen] for i in range(0,len(data[motif]),splitlen)]]
            number_of_groups = len(splitdata)
            expected = float(splitlen*scipy.prod(p))
            d_max = max([abs(datapoint-expected) for datapoint in splitdata])
            if 1-abs(scipy.stats.binom.cdf(expected+d_max-1,splitlen,scipy.prod(p)) - scipy.stats.binom.cdf(expected-d_max,splitlen,scipy.prod(p)))**number_of_groups < threshold:
                outlier_count += 1
        if outlier_count == 0:
            print('No outliers detected at threshold Pr < '+str(threshold)+', '+str(len(splitdata))+' samples of '+str(splitlen)+' runs each.')
        elif outlier_count == 1:
            print('1 possible outlier at threshold Pr < '+str(threshold)+', '+str(len(splitdata))+' samples of '+str(splitlen)+' runs each.')
        else:
            print(str(outlier_count)+' possible outliers at threshold Pr < '+str(threshold)+', '+str(len(splitdata))+' samples of '+str(splitlen)+' runs each.')
        
def makesuite(exhaustive=False,insane=False,performance=False,distribution_width=False):
    suite = unittest.TestSuite()
    suite.addTest(TestSampling("test_multilayer_partially_interconnected"))
    suite.addTest(TestSampling("test_default_required_lengths"))
    suite.addTest(TestSampling("test_default_check_reqs"))
    suite.addTest(TestSampling("test_dumb_enumeration"))
    suite.addTest(TestSampling("test_esu_concise"))
    if exhaustive:
        suite.addTest(TestSampling("test_esu_exhaustive"))
    if insane:
        suite.addTest(TestSampling("test_esu_insane"))
    if performance:
        suite.addTest(TestSampling("test_esu_performance"))
    if distribution_width:
        suite.addTest(TestSampling("test_esu_distribution_width"))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(makesuite(exhaustive=False,insane=False,performance=True,distribution_width=False))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    