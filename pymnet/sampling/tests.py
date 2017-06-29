# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import sys
import unittest
from pymnet import net
import reqs
import dumb

class TestSampling(unittest.TestCase):

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
            
    def test_dumb_enumeration(self):
        net1 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net2[1,'X'][1,'Y'] = 1
        net2[1,'X'][2,'X'] = 1
        net3 = net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        net3[1,'X'][1,'Y'] = 1
        net3[1,'X'][3,'X'] = 1
        net3[1,'Y'][2,'Z'] = 1
        resultlist = []
        dumb.dumbEnumeration(net1,[1,2],[1],resultlist)
        self.assertEqual(resultlist,[])
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

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSampling)
    unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite)