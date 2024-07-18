import sys
import unittest

import pymnet.graphlets as graphlets
from pymnet import isomorphisms, net


class TestGraphlets(unittest.TestCase):
    def setUp(self):
        self.M_ref_1 = net.MultiplexNetwork(
            couplings="categorical", fullyInterconnected=True
        )
        self.M_ref_1[42, 99, "x", "x"] = 1
        self.M_ref_1.add_layer("y")
        self.M_ref_2 = net.MultiplexNetwork(
            couplings="categorical", fullyInterconnected=True
        )
        self.M_ref_2[42, 99, "x", "x"] = 1
        self.M_ref_2[42, 99, "y", "y"] = 1

    def test_graphlets(self):
        nets, invs = graphlets.graphlets(
            n=3,
            layers=["a", "b", "c"],
            n_l=2,
            couplings="categorical",
            allowed_aspects="all",
        )
        assert len(nets[2]) == 2
        assert len(nets[3]) == 10
        # check that the two 2-node-2-layer graphlets match the reference nets
        match_ref_1 = False
        match_ref_2 = False
        for net in nets[2]:
            if isomorphisms.is_isomorphic(net, self.M_ref_1, allowed_aspects="all"):
                match_ref_1 = True
            elif isomorphisms.is_isomorphic(net, self.M_ref_2, allowed_aspects="all"):
                match_ref_2 = True
        assert match_ref_1
        assert match_ref_2


def makesuite():
    suite = unittest.TestSuite()
    suite.addTest(TestGraphlets("test_graphlets"))
    return suite


def test_graphlets(**kwargs):
    suite = makesuite(**kwargs)
    return unittest.TextTestRunner().run(suite).wasSuccessful()


if __name__ == "__main__":
    sys.exit(not test_graphlets())
