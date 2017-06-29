# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import unittest
import reqs

class TestRequirementChecks(unittest.TestCase):
    
    def test_required_lengths(self):
        self.assertEqual((reqs.calculate_required_lengths([4,3,4,2],[3,2,2,1,2,1,1,2,1,1,1])),(6,4))
        self.assertEqual((reqs.calculate_required_lengths([1],[])),(1,1))
        self.assertEqual((reqs.calculate_required_lengths([9999],[])),(9999,1))
        
        self.assertNotEqual((reqs.calculate_required_lengths([5,3,4,2],[3,2,2,1,2,1,1,2,1,1,1])),(6,4))
        
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([49,999],[])
        with self.assertRaises(AssertionError):
            reqs.calculate_required_lengths([],[])
        
        
if __name__ == '__main__':
    unittest.main()