# -*- coding: utf-8 -*-

import sys
import unittest
import time
import scipy,scipy.stats
from pymnet import net,models
from pymnet.sampling import reqs,dumb,esu,creators

class TestSampling(unittest.TestCase):
    
    def test_er_multilayer_partially_interconnected(self):
        nodelist = [[1,2,3],[2,3,4],[4,1,2]]
        net1 = creators.er_multilayer_partially_interconnected(nodelist,0)
        for nodelayer in list(net1.iter_node_layers()):
            self.assertEqual(net1[nodelayer[0],nodelayer[1]].deg(),0)
        net2 = creators.er_multilayer_partially_interconnected(nodelist,1)
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
        
    def test_default_check_reqs_less_or_equal(self):
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
        with self.assertRaises(AssertionError):
            reqs.default_check_reqs(net2,[1,2],['Y','X'],sizes=[1,2],intersections=[3],intersection_type="less_or_equal")
            reqs.default_check_reqs(net2,[1,2],['Y','X'],sizes=[1,2],intersections=[],nnodes=2,intersection_type="less_or_equal")
        self.assertFalse(reqs.default_check_reqs(net1,[1],['X'],sizes=[1],intersections=[],nnodes=1,nlayers=1,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net2,[1,2],['Y','X'],sizes=[1,2],intersections=[3],nnodes=2,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net3,[1,2,3],['X','Y','Z'],sizes=[2,2,1],intersections=[3,2,3,2],nnodes=3,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net3,[1,2,3],['X','Y','Z'],sizes=[2,2,1],intersections=[1,1,1,1],nnodes=3,intersection_type="less_or_equal"))
        self.assertFalse(reqs.default_check_reqs(net3,[1,2,3],['X','Y','Z'],sizes=[2,2,1],intersections=[0,1,1,0],nnodes=3,intersection_type="less_or_equal"))
        self.assertFalse(reqs.default_check_reqs(net4,[1,2],['X','Y','Z'],sizes=[2,2,2],intersections=[3,3,3,3],nnodes=2,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net5,[1,2],['X','Y','Z'],sizes=[2,2,2],intersections=[3,3,3,3],nnodes=2,intersection_type="less_or_equal"))
        self.assertFalse(reqs.default_check_reqs(net5,[1,2],['X','Y','Z'],sizes=[2,2,2],intersections=[2,2,2,1],nnodes=2,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net6,[1,0],['X','Z','Y'],sizes=[2,2,2],intersections=[3,2,3,3],nnodes=2,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net7,['X','Y'],['X','Y','Z'],sizes=[2,1,1],intersections=[3,3,3,3],nnodes=2,intersection_type="less_or_equal"))
        self.assertFalse(reqs.default_check_reqs(net7,['X','Y'],['X','Y','Z'],sizes=[2,2,1],intersections=[3,3,3,3],nnodes=2,intersection_type="less_or_equal"))

    def test_default_check_reqs_with_None_in_intersections(self):
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
        self.assertFalse(reqs.default_check_reqs(net1,[1],['X'],sizes=[1],intersections=[None],nnodes=1,nlayers=1))
        self.assertFalse(reqs.default_check_reqs(net1,[1],['X','Y'],sizes=[1,1],intersections=[None],nnodes=1,nlayers=2))
        self.assertTrue(reqs.default_check_reqs(net2,[1,2],['X','Y'],sizes=[2,1],intersections=[None],nnodes=2,nlayers=2))
        self.assertTrue(reqs.default_check_reqs(net3,[1,2,3],['X','Y','Z'],sizes=[2,2,1],intersections=[1,None,1,1],nnodes=3,nlayers=3))
        self.assertTrue(reqs.default_check_reqs(net3,[1,2,3],['X','Y','Z'],sizes=[2,2,1],intersections=[1,None,None,None],nnodes=3,nlayers=3))
        self.assertFalse(reqs.default_check_reqs(net3,[1,2,3],['X','Y','Z'],sizes=[2,2,1],intersections=[2,None,1,1],nnodes=3,nlayers=3))
        self.assertTrue(reqs.default_check_reqs(net3,[1,2,3],['X','Y','Z'],sizes=[2,2,1],intersections=[2,None,1,1],nnodes=3,nlayers=3,intersection_type="less_or_equal"))
        self.assertFalse(reqs.default_check_reqs(net4,[1,2],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,None],nnodes=2,nlayers=3))
        self.assertTrue(reqs.default_check_reqs(net5,[1,2],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,None],nnodes=2,nlayers=3))
        self.assertFalse(reqs.default_check_reqs(net5,[1,2],['X','Y','Z'],sizes=[2,2,2],intersections=[None,1,None,None],nnodes=2,nlayers=3))
        self.assertTrue(reqs.default_check_reqs(net6,[0,1],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,None],nnodes=2,nlayers=3))
        self.assertTrue(reqs.default_check_reqs(net7,['X','Y'],['X','Y','Z'],sizes=[1,2,1],intersections=[1,None,None,1],nnodes=2,nlayers=3))
        self.assertFalse(reqs.default_check_reqs(net7,['X','Z'],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,None],nnodes=2,nlayers=3))
        self.assertTrue(reqs.default_check_reqs(net7,['X','Y','Z'],['X','Y','Z'],sizes=[3,2,2],intersections=[2,None,None,None],nnodes=3,nlayers=3))
        self.assertTrue(reqs.default_check_reqs(net7,['X','Y','Z'],['X','Y','Z'],sizes=[3,2,2],intersections=[2,2,2,None],nnodes=3,nlayers=3))
        self.assertFalse(reqs.default_check_reqs(net7,['X','Y','Z'],['X','Y','Z'],sizes=[3,2,2],intersections=[None,None,None,3],nnodes=3,nlayers=3))
        self.assertTrue(reqs.default_check_reqs(net7,['X','Y','Z'],['X','Y','Z'],sizes=[3,2,2],intersections=[None,None,None,3],nnodes=3,nlayers=3,intersection_type="less_or_equal"))
        self.assertFalse(reqs.default_check_reqs(net7,['X','Y','Z'],['X','Y','Z'],sizes=[3,2,2],intersections=[None,None,None,1],nnodes=3,nlayers=3,intersection_type="less_or_equal"))

    def test_default_check_reqs_only_common_intersection(self):
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2[1,'X'][1,'Y'] = 1
        net2[1,'X'][2,'X'] = 1
        net3 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net3[1,'X'][2,'X'] = 1
        net3[1,'X'][1,'Y'] = 1
        net3[1,'Y'][1,'Z'] = 1
        net3[1,'Z'][2,'Z'] = 1
        net3[2,'Z'][2,'Y'] = 1
        net4 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net4['X','X']['Z','X'] = 1
        net4['X','X']['X','Z'] = 1
        net4['X','Z']['Y','Z'] = 1
        net4['X','Z']['X','Y'] = 1
        net4['Y','Z']['Z','Z'] = 1
        net4['X','Y']['Z','Y'] = 1
        self.assertFalse(reqs.default_check_reqs(net1,[1],['X'],sizes=[1],intersections=[],nnodes=1,nlayers=1))
        self.assertTrue(reqs.default_check_reqs(net2,[1,2],['X','Y'],sizes=[1,2],intersections=[1],nnodes=2,nlayers=2))
        self.assertTrue(reqs.default_check_reqs(net3,[2,1],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,2],nnodes=2,nlayers=3))
        self.assertFalse(reqs.default_check_reqs(net3,[2,1],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,3],nnodes=2,nlayers=3))
        self.assertFalse(reqs.default_check_reqs(net3,[2,1],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,1],nnodes=2,nlayers=3))
        self.assertTrue(reqs.default_check_reqs(net4,['X','Y','Z'],['X','Y','Z'],sizes=[2,3,2],intersections=[None,None,None,2],nnodes=3,nlayers=3))
        self.assertFalse(reqs.default_check_reqs(net4,['X','Y','Z'],['X','Y','Z'],sizes=[2,3,2],intersections=[None,None,None,3],nnodes=3,nlayers=3))
        self.assertFalse(reqs.default_check_reqs(net4,['X','Y','Z'],['X','Y','Z'],sizes=[2,3,2],intersections=[None,None,None,1],nnodes=3,nlayers=3))
    
    def test_default_check_reqs_only_common_intersection_less_or_equal(self):
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2[1,'X'][1,'Y'] = 1
        net2[1,'X'][2,'X'] = 1
        net3 = net.MultilayerNetwork(aspects=1,fullyInterconnected=True)
        net3[1,'X'][2,'X'] = 1
        net3[1,'X'][1,'Y'] = 1
        net3[1,'Y'][1,'Z'] = 1
        net3[1,'Z'][2,'Z'] = 1
        net3[2,'Z'][2,'Y'] = 1
        net4 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net4['X','X']['Z','X'] = 1
        net4['X','X']['X','Z'] = 1
        net4['X','Z']['Y','Z'] = 1
        net4['X','Z']['X','Y'] = 1
        net4['Y','Z']['Z','Z'] = 1
        net4['X','Y']['Z','Y'] = 1
        self.assertFalse(reqs.default_check_reqs(net1,[1],['X'],sizes=[1],intersections=[2],nnodes=1,nlayers=1,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net2,[1,2],['X','Y'],sizes=[1,2],intersections=[2],nnodes=2,nlayers=2,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net3,[2,1],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,2],nnodes=2,nlayers=3,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net3,[2,1],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,3],nnodes=2,nlayers=3,intersection_type="less_or_equal"))
        self.assertFalse(reqs.default_check_reqs(net3,[2,1],['X','Y','Z'],sizes=[2,2,2],intersections=[None,None,None,1],nnodes=2,nlayers=3,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net4,['X','Y','Z'],['X','Y','Z'],sizes=[2,3,2],intersections=[None,None,None,2],nnodes=3,nlayers=3,intersection_type="less_or_equal"))
        self.assertTrue(reqs.default_check_reqs(net4,['X','Y','Z'],['X','Y','Z'],sizes=[2,3,2],intersections=[None,None,None,3],nnodes=3,nlayers=3,intersection_type="less_or_equal"))
        self.assertFalse(reqs.default_check_reqs(net4,['X','Y','Z'],['X','Y','Z'],sizes=[2,3,2],intersections=[None,None,None,1],nnodes=3,nlayers=3,intersection_type="less_or_equal"))

    def test_relaxed_check_reqs(self):
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net1['X','X']['Z','X'] = 1
        net1['X','X']['X','Z'] = 1
        net1['X','Z']['Y','Z'] = 1
        net1['X','Z']['X','Y'] = 1
        net1['Y','Z']['Z','Z'] = 1
        net1['X','Y']['Z','Y'] = 1
        self.assertFalse(reqs.relaxed_check_reqs(net1,['X','Z'],['X','Y']))
        self.assertTrue(reqs.relaxed_check_reqs(net1,['X','Z','Y'],['X','Z']))
        self.assertTrue(reqs.relaxed_check_reqs(net1,['X','Y'],['Z']))
        self.assertFalse(reqs.relaxed_check_reqs(net1,['X','Y'],['X']))
        self.assertFalse(reqs.relaxed_check_reqs(net1,['X','Y','W'],['Z']))
        self.assertFalse(reqs.relaxed_check_reqs(net1,['X','Z','Y'],['X','Z','W']))

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
        net9 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net9[1,'X'][1,'Y'] = 1
        net9[1,'X'][2,'X'] = 1
        net9.add_node(2,layer='Y')
        net9[1,'X'][3,'X'] = 1
        net9[1,'Y'][1,'Z'] = 1
        net9[1,'X'][4,'X'] = 1
        net9[1,'Z'][4,'Z'] = 1
        net9[4,'Z'][5,'Z'] = 1
        net9[1,'Z'][4,'Y'] = 1
        resultlist = []
        with self.assertRaises(AssertionError):
            dumb.dumb_enumeration(net2,resultlist,sizes=[],intersections=[])
        with self.assertRaises(AssertionError):
            dumb.dumb_enumeration(net2,resultlist,sizes=[2,1],intersections=[1,1])
        with self.assertRaises(AssertionError):
            dumb.dumb_enumeration(net2,resultlist,sizes=[2,1],intersections=[])
        with self.assertRaises(AssertionError):
            dumb.dumb_enumeration(net2,resultlist,sizes=[2,1,1],intersections=[1])
        with self.assertRaises(AssertionError):
            dumb.dumb_enumeration(net2,resultlist,sizes=[],intersections=[1])
        resultlist = []
        dumb.dumb_enumeration(net1,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net2,resultlist,sizes=[1],intersections=[])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X']),([1],['Y']),([2],['X'])])
        resultlist = []
        dumb.dumb_enumeration(net2,resultlist,sizes=[1,2],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net2,resultlist,sizes=[2,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[1,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y']),([1],['Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,1,1],intersections=[1,0,0,0])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,1,2],intersections=[1,1,1,1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net4,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net4,resultlist,sizes=[2,2],intersections=[2])
        self.assertEqual(resultlist,[])
        resultlist =  []
        dumb.dumb_enumeration(net5,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist =  []
        dumb.dumb_enumeration(net5,resultlist,sizes=[2,2],intersections=[2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0, 1], ['X', 'Y']), ([0, 1], ['X', 'Z']), ([0, 1], ['Y', 'Z'])])
        resultlist = []
        dumb.dumb_enumeration(net6,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net7,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net8,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,2,1],intersections=[1,None,None,None],nnodes=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net6,resultlist,sizes=[2,2],intersections=[None],nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net9,resultlist,sizes=[3,2,2],intersections=[None,None,2,None],nnodes=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3,4],['X','Y','Z']),([1,4,5],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net9,resultlist,sizes=[1,2,1],intersections=[1,None,1,None],nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net9,resultlist,sizes=[1,2,1],intersections=[1,None,1,None],nnodes=3)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net9,resultlist,sizes=[1,2,1],intersections=[0,None,1,None],nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net2,resultlist,sizes=[1,2],intersections=[2],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[1,2,2],intersections=[2,2,2,2],nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[1,2],intersections=[2],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[1,2,1],intersections=[2,1,1,1],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z']),([1,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net4,resultlist,sizes=[2,2],intersections=[2],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net5,resultlist,sizes=[2,2,2],intersections=[2,2,2,1],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net5,resultlist,sizes=[2,2,2],intersections=[2,2,2,3],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net6,resultlist,sizes=[2,2,2],intersections=[2,2,2,3],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net7,resultlist,sizes=[2,2,2],intersections=[2,2,2,3],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[1,2,2],intersections=[None,None,None,2],nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[1,1,1],intersections=[None,None,None,None],nnodes=1,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[1,2,2],intersections=[3,None,None,None],nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[1,2,2],intersections=[None,None,None,0],nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[1,2,1],intersections=[None,2,2,2],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z']),([1,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net6,resultlist,sizes=[2,2,2],intersections=[None,2,None,None],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        
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
        net9 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net9[1,'X'][1,'Y'] = 1
        net9[1,'X'][2,'X'] = 1
        net9.add_node(2,layer='Y')
        net9[1,'X'][3,'X'] = 1
        net9[1,'Y'][1,'Z'] = 1
        net9[1,'X'][4,'X'] = 1
        net9[1,'Z'][4,'Z'] = 1
        net9[4,'Z'][5,'Z'] = 1
        net9[1,'Z'][4,'Y'] = 1
        resultlist = []
        with self.assertRaises(AssertionError):
            esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[],intersections=[])
        with self.assertRaises(AssertionError):
            esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[2,1],intersections=[1,1])
        with self.assertRaises(AssertionError):
            esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[2,1],intersections=[])
        with self.assertRaises(AssertionError):
            esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[2,1,1],intersections=[1])
        with self.assertRaises(AssertionError):
            esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[],intersections=[1])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net1,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[1],intersections=[])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X']),([1],['Y']),([2],['X'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[1,2],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[2,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[1,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y']),([1],['Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,1],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,1,1],intersections=[1,0,0,0])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,1,2],intersections=[1,1,1,1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net4,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net4,resultlist,sizes=[2,2],intersections=[2])
        self.assertEqual(resultlist,[])
        resultlist =  []
        esu.sample_multilayer_subgraphs_esu(net5,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist =  []
        esu.sample_multilayer_subgraphs_esu(net5,resultlist,sizes=[2,2],intersections=[2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0, 1], ['X', 'Y']), ([0, 1], ['X', 'Z']), ([0, 1], ['Y', 'Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net6,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net7,resultlist,sizes=[2,2,2],intersections=[2,2,2,2])
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net8,resultlist,sizes=[1,2],intersections=[1])
        self.assertEqual(resultlist,[])
        
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,2,1],intersections=[1,None,None,None],nnodes=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net6,resultlist,sizes=[2,2],intersections=[None],nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net9,resultlist,sizes=[3,2,2],intersections=[None,None,2,None],nnodes=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3,4],['X','Y','Z']),([1,4,5],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net9,resultlist,sizes=[1,2,1],intersections=[1,None,1,None],nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net9,resultlist,sizes=[1,2,1],intersections=[1,None,1,None],nnodes=3)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net9,resultlist,sizes=[1,2,1],intersections=[0,None,1,None],nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[1,2],intersections=[2],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[1,2,2],intersections=[2,2,2,2],nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[1,2],intersections=[2],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[1,2,1],intersections=[2,1,1,1],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z']),([1,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net4,resultlist,sizes=[2,2],intersections=[2],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net5,resultlist,sizes=[2,2,2],intersections=[2,2,2,1],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net5,resultlist,sizes=[2,2,2],intersections=[2,2,2,3],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net6,resultlist,sizes=[2,2,2],intersections=[2,2,2,3],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net7,resultlist,sizes=[2,2,2],intersections=[2,2,2,3],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[1,2,2],intersections=[None,None,None,2],nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[1,1,1],intersections=[None,None,None,None],nnodes=1,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[1,2,2],intersections=[3,None,None,None],nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[1,2,2],intersections=[None,None,None,0],nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[1,2,1],intersections=[None,2,2,2],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z']),([1,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net6,resultlist,sizes=[2,2,2],intersections=[None,2,None,None],nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        
    def test_dumb_enumeration_relaxed(self):
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
            dumb.dumb_enumeration(net2,resultlist,nnodes=1)
            dumb.dumb_enumeration(net2,resultlist,nlayers=1)
        resultlist = []
        dumb.dumb_enumeration(net1,resultlist,nnodes=1,nlayers=1)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net2,resultlist,nnodes=1,nlayers=1)
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X']),([1],['Y']),([2],['X'])])
        resultlist = []
        dumb.dumb_enumeration(net2,resultlist,nnodes=2,nlayers=1)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        self.assertEqual(resultlist,[([1,2],['X'])])
        resultlist = []
        dumb.dumb_enumeration(net2,resultlist,nnodes=2,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        self.assertEqual(resultlist,[([1,2,],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,nnodes=2,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,nnodes=3,nlayers=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,nnodes=1,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,nnodes=1,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y']),([1],['Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,nnodes=3,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net4,resultlist,nnodes=2,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net5,resultlist,nnodes=2,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y']),([0,1],['X','Z']),([0,1],['Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net5,resultlist,nnodes=2,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net6,resultlist,nnodes=2,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net6,resultlist,nnodes=1,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net7,resultlist,nnodes=2,nlayers=3)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net8,resultlist,nnodes=2,nlayers=2)
        self.assertEqual(resultlist,[])        

    def test_esu_relaxed_concise(self):
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
            esu.sample_multilayer_subgraphs_esu(net2,resultlist,nnodes=1)
            esu.sample_multilayer_subgraphs_esu(net2,resultlist,nlayers=1)
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net1,resultlist,nnodes=1,nlayers=1)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net2,resultlist,nnodes=1,nlayers=1)
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X']),([1],['Y']),([2],['X'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net2,resultlist,nnodes=2,nlayers=1)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        self.assertEqual(resultlist,[([1,2],['X'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net2,resultlist,nnodes=2,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        self.assertEqual(resultlist,[([1,2,],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,nnodes=2,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,nnodes=3,nlayers=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,nnodes=1,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,nnodes=1,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y']),([1],['Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,nnodes=3,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net4,resultlist,nnodes=2,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net5,resultlist,nnodes=2,nlayers=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y']),([0,1],['X','Z']),([0,1],['Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net5,resultlist,nnodes=2,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net6,resultlist,nnodes=2,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net6,resultlist,nnodes=1,nlayers=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net7,resultlist,nnodes=2,nlayers=3)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net8,resultlist,nnodes=2,nlayers=2)
        self.assertEqual(resultlist,[])
        
    def test_dumb_enumeration_only_common_intersection_concise(self):
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
        net9 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net9[1,'X'][1,'Y'] = 1
        net9[1,'X'][2,'X'] = 1
        net9.add_node(2,layer='Y')
        net9[1,'X'][3,'X'] = 1
        net9[1,'Y'][1,'Z'] = 1
        net9[1,'X'][4,'X'] = 1
        net9[1,'Z'][4,'Z'] = 1
        net9[4,'Z'][5,'Z'] = 1
        net9[1,'Z'][4,'Y'] = 1
        net10 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net10[1,'X'][2,'X'] = 1
        net10[2,'X'][2,'Y'] = 1
        net10[2,'Y'][3,'Y'] = 1
        net10[3,'X'][3,'Y'] = 1
        net10[3,'Y'][3,'Z'] = 1
        net10[3,'Z'][4,'Z'] = 1
        net10[5,'X'][6,'Y'] = 1
        net10[6,'X'][6,'Y'] = 1
        net10[6,'Y'][6,'Z'] = 1
        net10[6,'Z'][7,'Z'] = 1
        net10[6,'Y'][8,'Z'] = 1
        net10[6,'Z'][5,'Y'] = 1
        net11 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net11[1,'X'][2,'X'] = 1
        net11[2,'X'][3,'X'] = 1
        net11[1,'X'][1,'Y'] = 1
        net11[1,'Y'][2,'Y'] = 1
        net11[1,'Y'][1,'Z'] = 1
        net11[1,'Z'][3,'Z'] = 1
        net11.add_node(4,layer='W')
        resultlist = []
        dumb.dumb_enumeration(net1,resultlist,sizes=[1,1],intersections=1,nnodes=1)
        self.assertEqual(resultlist,[])
        dumb.dumb_enumeration(net2,resultlist,sizes=[1,1],intersections=1,nnodes=1)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        self.assertEqual(resultlist,[([1],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net2,resultlist,sizes=[1,2],intersections=1,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,1],intersections=1,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,1,1],intersections=1,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z']),([1,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,2,1],intersections=1,nnodes=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net4,resultlist,sizes=[2,2],intersections=1,nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net5,resultlist,sizes=[2,2,2],intersections=2,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net5,resultlist,sizes=[1,1,1],intersections=1,nnodes=1)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0],['X','Y','Z']),([1],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net5,resultlist,sizes=[1,2,1],intersections=1,nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net6,resultlist,sizes=[2,2,2],intersections=2,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net7,resultlist,sizes=[2,2,2],intersections=2,nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net8,resultlist,sizes=[2,2],intersections=2,nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net9,resultlist,sizes=[3,3,2],intersections=2,nnodes=4)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3,4,5],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net10,resultlist,sizes=[3,2,2],intersections=1,nnodes=4)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3,4],['X','Y','Z']),([5,6,7,8],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net11,resultlist,sizes=[3,2,2],intersections=1,nnodes=4)
        self.assertEqual(resultlist,[])
        
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,1,2],intersections=2,nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,1,2],intersections=2,nnodes=0,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,1],intersections=2,nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net3,resultlist,sizes=[2,1],intersections=2,nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        dumb.dumb_enumeration(net9,resultlist,sizes=[2,2],intersections=3,nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,4],['Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net9,resultlist,sizes=[2,2,3],intersections=3,nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3,4],['X','Y','Z']),([1,4,5],['X','Y','Z'])])
        resultlist = []
        dumb.dumb_enumeration(net9,resultlist,sizes=[2,2,3],intersections=1,nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        
    def test_esu_only_common_intersection_concise(self):
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
        net9 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net9[1,'X'][1,'Y'] = 1
        net9[1,'X'][2,'X'] = 1
        net9.add_node(2,layer='Y')
        net9[1,'X'][3,'X'] = 1
        net9[1,'Y'][1,'Z'] = 1
        net9[1,'X'][4,'X'] = 1
        net9[1,'Z'][4,'Z'] = 1
        net9[4,'Z'][5,'Z'] = 1
        net9[1,'Z'][4,'Y'] = 1
        net10 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net10[1,'X'][2,'X'] = 1
        net10[2,'X'][2,'Y'] = 1
        net10[2,'Y'][3,'Y'] = 1
        net10[3,'X'][3,'Y'] = 1
        net10[3,'Y'][3,'Z'] = 1
        net10[3,'Z'][4,'Z'] = 1
        net10[5,'X'][6,'Y'] = 1
        net10[6,'X'][6,'Y'] = 1
        net10[6,'Y'][6,'Z'] = 1
        net10[6,'Z'][7,'Z'] = 1
        net10[6,'Y'][8,'Z'] = 1
        net10[6,'Z'][5,'Y'] = 1
        net11 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net11[1,'X'][2,'X'] = 1
        net11[2,'X'][3,'X'] = 1
        net11[1,'X'][1,'Y'] = 1
        net11[1,'Y'][2,'Y'] = 1
        net11[1,'Y'][1,'Z'] = 1
        net11[1,'Z'][3,'Z'] = 1
        net11.add_node(4,layer='W')
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net1,resultlist,sizes=[1,1],intersections=1,nnodes=1)
        self.assertEqual(resultlist,[])
        esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[1,1],intersections=1,nnodes=1)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        self.assertEqual(resultlist,[([1],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net2,resultlist,sizes=[1,2],intersections=1,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        self.assertEqual(resultlist,[([1,2],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,1],intersections=1,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,1,1],intersections=1,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z']),([1,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,2,1],intersections=1,nnodes=3)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net4,resultlist,sizes=[2,2],intersections=1,nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net5,resultlist,sizes=[2,2,2],intersections=2,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0,1],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net5,resultlist,sizes=[1,1,1],intersections=1,nnodes=1)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([0],['X','Y','Z']),([1],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net5,resultlist,sizes=[1,2,1],intersections=1,nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net6,resultlist,sizes=[2,2,2],intersections=2,nnodes=2)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net7,resultlist,sizes=[2,2,2],intersections=2,nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net8,resultlist,sizes=[2,2],intersections=2,nnodes=2)
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net9,resultlist,sizes=[3,3,2],intersections=2,nnodes=4)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3,4,5],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net10,resultlist,sizes=[3,2,2],intersections=1,nnodes=4)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3,4],['X','Y','Z']),([5,6,7,8],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net11,resultlist,sizes=[3,2,2],intersections=1,nnodes=4)
        self.assertEqual(resultlist,[])
        
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,1,2],intersections=2,nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2,3],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,1,2],intersections=2,nnodes=0,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,1],intersections=2,nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net3,resultlist,sizes=[2,1],intersections=2,nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net9,resultlist,sizes=[2,2],intersections=3,nnodes=2,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,4],['Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net9,resultlist,sizes=[2,2,3],intersections=3,nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3,4],['X','Y','Z']),([1,4,5],['X','Y','Z'])])
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net9,resultlist,sizes=[2,2,3],intersections=1,nnodes=3,intersection_type="less_or_equal")
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[])
        
    def test_dumb_callback(self):
        #def callback_fun((nodelist,layerlist),resultlist):
        def callback_fun(nodelist_layerlist,resultlist):
            nodelist,layerlist=nodelist_layerlist
            resultlist.append((nodelist,layerlist))
            return
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net1[1,'X'][1,'Y'] = 1
        net1[1,'X'][3,'X'] = 1
        net1[1,'Y'][1,'Z'] = 1
        net1[1,'Y'][2,'Z'] = 1
        resultlist = []
        dumb.dumb_enumeration(net1,lambda x: callback_fun(x,resultlist),sizes=[1,2],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
        
    def test_esu_callback(self):
        #def callback_fun((nodelist,layerlist),resultlist):
        def callback_fun(nodelist_layerlist,resultlist):
            nodelist,layerlist=nodelist_layerlist
            resultlist.append((nodelist,layerlist))
            return
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net1[1,'X'][1,'Y'] = 1
        net1[1,'X'][3,'X'] = 1
        net1[1,'Y'][1,'Z'] = 1
        net1[1,'Y'][2,'Z'] = 1
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net1,lambda x: callback_fun(x,resultlist),sizes=[1,2],intersections=[1])
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,2],['Y','Z']),([1,3],['X','Y'])])
    
    def test_dumb_custom_check_function(self):
        def custom_check(network,nodelist,layerlist):
            if 3 in nodelist:
                return True
            else:
                return False
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net1[1,'X'][1,'Y'] = 1
        net1[1,'X'][3,'X'] = 1
        net1[1,'Y'][1,'Z'] = 1
        net1[1,'Y'][2,'Z'] = 1
        resultlist = []
        dumb.dumb_enumeration(net1,resultlist,nnodes=2,nlayers=3,custom_check_function=custom_check)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3],['X','Y','Z']),([2,3],['X','Y','Z'])])
    
    def test_esu_custom_check_function(self):
        def custom_check(network,nodelist,layerlist):
            if 3 in nodelist:
                return True
            else:
                return False
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net1[1,'X'][1,'Y'] = 1
        net1[1,'X'][3,'X'] = 1
        net1[1,'Y'][1,'Z'] = 1
        net1[1,'Y'][2,'Z'] = 1
        resultlist = []
        esu.sample_multilayer_subgraphs_esu(net1,resultlist,nnodes=2,nlayers=3,custom_check_function=custom_check)
        for result in resultlist:
            result[0].sort()
            result[1].sort()
        resultlist.sort()
        self.assertEqual(resultlist,[([1,3],['X','Y','Z'])])
        
    def test_esu_exhaustive(self):
        reqlist = [([1,1],[0]),([1,2],[0]),([1,2],[1]),([2,3],[1]),([2,1,1],[1,0,0,0])]
        for requirement in reqlist:
            for _ in range(30):
                network = creators.er_multilayer_partially_interconnected(creators.random_nodelists(30,10,5),0.05)
                resultlist_dumb = []
                resultlist_esu = []
                dumb.dumb_enumeration(network,resultlist_dumb,sizes=requirement[0],intersections=requirement[1])
                esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,sizes=requirement[0],intersections=requirement[1])
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
            for _ in range(100):
                network = creators.er_multilayer_partially_interconnected(creators.random_nodelists(30,10,5),0.05)
                resultlist_dumb = []
                resultlist_esu = []
                dumb.dumb_enumeration(network,resultlist_dumb,sizes=requirement[0],intersections=requirement[1])
                esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,sizes=requirement[0],intersections=requirement[1])
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
        for _ in range(10):
            for requirement in reqlist:
                resultlist_esu = []
                esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,sizes=requirement[0],intersections=requirement[1])
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
            esu.sample_multilayer_subgraphs_esu(network,resultlist,p=p,sizes=motif[0],intersections=motif[1])
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
        
    def test_esu_distribution_width(self,network=None,threshold=0.05,iterations=10000,motif=([2,1],[1]),splitlen=200,p=None,all_subgraphs=None):
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
        if network == None:
            network = creators.er_multilayer_partially_interconnected(creators.random_nodelists(100,30,10,seed=1),0.05,seed=1)       
        if p == None:
            req_nodelist_len,req_layerlist_len = reqs.default_calculate_required_lengths(sizes=motif[0],intersections=motif[1])
            p = [0.5] * (req_nodelist_len-1 + req_layerlist_len-1 + 1)
        if all_subgraphs == None:
            all_subgraphs = []
            esu.sample_multilayer_subgraphs_esu(network,all_subgraphs,sizes=motif[0],intersections=motif[1])
        data = self._statistical_sample(network,iterations,motif,p,all_subgraphs)
        outlier_count = 0
        motif_count = len(data)
        for motif_instance in data:
            splitdata = [sum(split) for split in [data[motif_instance][i:i+splitlen] for i in range(0,len(data[motif_instance]),splitlen)]]
            number_of_groups = len(splitdata)
            expected = float(splitlen*scipy.prod(p))
            d_max = max([abs(datapoint-expected) for datapoint in splitdata])
            if 1-abs(scipy.stats.binom.cdf(expected+d_max-1,splitlen,scipy.prod(p)) - scipy.stats.binom.cdf(expected-d_max,splitlen,scipy.prod(p)))**number_of_groups < threshold/float(motif_count):
                outlier_count += 1
        if outlier_count == 0:
            print('No outliers detected at threshold FWER <= '+str(threshold)+', Bonferroni correction used ('+str(motif_count)+' tests, '+str(len(splitdata))+' samples of '+str(splitlen)+' runs each).')
        elif outlier_count == 1:
            print('1 possible outlier at threshold FWER <= '+str(threshold)+', Bonferroni correction used ('+str(motif_count)+' tests, '+str(len(splitdata))+' samples of '+str(splitlen)+' runs each).')
        else:
            print(str(outlier_count)+' possible outliers at threshold FWER <= '+str(threshold)+', Bonferroni correction used ('+str(motif_count)+' tests, '+str(len(splitdata))+' samples of '+str(splitlen)+' runs each).')
        
    def test_different_parameter_sets(self):
        for _ in range(50):
            network = creators.er_multilayer_partially_interconnected(creators.random_nodelists(45,15,5),0.05)
            resultlist_dumb = []
            resultlist_esu = []
            dumb.dumb_enumeration(network,resultlist_dumb,sizes=[2,1],intersections=[1])
            esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,sizes=[2,1],intersections=[1])
            for result in resultlist_dumb:
                result[0].sort()
                result[1].sort()
            resultlist_dumb.sort()
            for result in resultlist_esu:
                result[0].sort()
                result[1].sort()
            resultlist_esu.sort()
            self.assertEqual(resultlist_dumb,resultlist_esu)
            resultlist_dumb = []
            resultlist_esu = []
            dumb.dumb_enumeration(network,resultlist_dumb,sizes=[3,2,2],intersections=1,nnodes=4)
            esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,sizes=[3,2,2],intersections=1,nnodes=4)
            for result in resultlist_dumb:
                result[0].sort()
                result[1].sort()
            resultlist_dumb.sort()
            for result in resultlist_esu:
                result[0].sort()
                result[1].sort()
            resultlist_esu.sort()
            self.assertEqual(resultlist_dumb,resultlist_esu)
            resultlist_dumb = []
            resultlist_esu = []
            dumb.dumb_enumeration(network,resultlist_dumb,sizes=[3,2,2],intersections=2,nnodes=4,intersection_type="less_or_equal")
            esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,sizes=[3,2,2],intersections=2,nnodes=4,intersection_type="less_or_equal")
            for result in resultlist_dumb:
                result[0].sort()
                result[1].sort()
            resultlist_dumb.sort()
            for result in resultlist_esu:
                result[0].sort()
                result[1].sort()
            resultlist_esu.sort()
            self.assertEqual(resultlist_dumb,resultlist_esu)
            resultlist_dumb = []
            resultlist_esu = []
            dumb.dumb_enumeration(network,resultlist_dumb,sizes=[2,2,2],intersections=[2,2,2,2],nnodes=4,intersection_type="less_or_equal")
            esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,sizes=[2,2,2],intersections=[2,2,2,2],nnodes=4,intersection_type="less_or_equal")
            for result in resultlist_dumb:
                result[0].sort()
                result[1].sort()
            resultlist_dumb.sort()
            for result in resultlist_esu:
                result[0].sort()
                result[1].sort()
            resultlist_esu.sort()
            self.assertEqual(resultlist_dumb,resultlist_esu)
            resultlist_dumb = []
            resultlist_esu = []
            dumb.dumb_enumeration(network,resultlist_dumb,nnodes=3,nlayers=3)
            esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,nnodes=3,nlayers=3)
            for result in resultlist_dumb:
                result[0].sort()
                result[1].sort()
            resultlist_dumb.sort()
            for result in resultlist_esu:
                result[0].sort()
                result[1].sort()
            resultlist_esu.sort()
            self.assertEqual(resultlist_dumb,resultlist_esu)
            resultlist_dumb = []
            resultlist_esu = []
            dumb.dumb_enumeration(network,resultlist_dumb,sizes=[2,3,2],intersections=[2,1,None,None],nnodes=4)
            esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,sizes=[2,3,2],intersections=[2,1,None,None],nnodes=4)
            for result in resultlist_dumb:
                result[0].sort()
                result[1].sort()
            resultlist_dumb.sort()
            for result in resultlist_esu:
                result[0].sort()
                result[1].sort()
            resultlist_esu.sort()
            self.assertEqual(resultlist_dumb,resultlist_esu)
            resultlist_dumb = []
            resultlist_esu = []
            dumb.dumb_enumeration(network,resultlist_dumb,sizes=[2,3,2],intersections=[2,1,None,None],nnodes=4,intersection_type="less_or_equal")
            esu.sample_multilayer_subgraphs_esu(network,resultlist_esu,sizes=[2,3,2],intersections=[2,1,None,None],nnodes=4,intersection_type="less_or_equal")
            for result in resultlist_dumb:
                result[0].sort()
                result[1].sort()
            resultlist_dumb.sort()
            for result in resultlist_esu:
                result[0].sort()
                result[1].sort()
            resultlist_esu.sort()
            self.assertEqual(resultlist_dumb,resultlist_esu)

def makesuite(exhaustive=False,insane=False,performance=False,distribution_width=False,parameter_sets=False):
    suite = unittest.TestSuite()
    suite.addTest(TestSampling("test_er_multilayer_partially_interconnected"))
    suite.addTest(TestSampling("test_default_required_lengths"))
    suite.addTest(TestSampling("test_default_check_reqs"))
    suite.addTest(TestSampling("test_default_check_reqs_less_or_equal"))
    suite.addTest(TestSampling("test_default_check_reqs_with_None_in_intersections"))
    suite.addTest(TestSampling("test_default_check_reqs_only_common_intersection"))
    suite.addTest(TestSampling("test_default_check_reqs_only_common_intersection_less_or_equal"))
    suite.addTest(TestSampling("test_relaxed_check_reqs"))
    suite.addTest(TestSampling("test_dumb_enumeration"))
    suite.addTest(TestSampling("test_esu_concise"))
    suite.addTest(TestSampling("test_dumb_enumeration_relaxed"))
    suite.addTest(TestSampling("test_esu_relaxed_concise"))
    suite.addTest(TestSampling("test_dumb_enumeration_only_common_intersection_concise"))
    suite.addTest(TestSampling("test_esu_only_common_intersection_concise"))
    suite.addTest(TestSampling("test_dumb_callback"))
    suite.addTest(TestSampling("test_esu_callback"))
    suite.addTest(TestSampling("test_dumb_custom_check_function"))
    suite.addTest(TestSampling("test_esu_custom_check_function"))
    if exhaustive:
        suite.addTest(TestSampling("test_esu_exhaustive"))
    if insane:
        suite.addTest(TestSampling("test_esu_insane"))
    if performance:
        suite.addTest(TestSampling("test_esu_performance"))
    if distribution_width:
        suite.addTest(TestSampling("test_esu_distribution_width"))
    if parameter_sets:
        suite.addTest(TestSampling("test_different_parameter_sets"))
    return suite

def test_sampling(**kwargs):
    suite=makesuite(**kwargs)
    return unittest.TextTestRunner().run(suite).wasSuccessful()

if __name__ == '__main__':
    sys.exit(not test_sampling(exhaustive=False,insane=False,performance=False,distribution_width=False,parameter_sets=False))
