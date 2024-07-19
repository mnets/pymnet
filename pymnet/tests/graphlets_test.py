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

    ### tests for graphlets file

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

    def test_automorphism_orbits(self):
        nets, invs = graphlets.graphlets(
            n=3,
            layers=["a", "b", "c"],
            n_l=2,
            couplings="categorical",
            allowed_aspects="all",
        )
        auts = graphlets.automorphism_orbits(nets, allowed_aspects="all")
        target_auts = {
            (3, 0, 2): 1,
            (3, 9, 0): 0,
            (3, 4, 0): 0,
            (3, 3, 1): 0,
            (3, 4, 1): 1,
            (3, 3, 0): 0,
            (3, 4, 2): 1,
            (3, 3, 2): 0,
            (3, 8, 0): 0,
            (3, 7, 1): 0,
            (3, 8, 1): 1,
            (3, 2, 2): 2,
            (3, 7, 0): 0,
            (2, 0, 1): 0,
            (3, 8, 2): 1,
            (3, 1, 2): 1,
            (3, 2, 0): 0,
            (3, 7, 2): 2,
            (3, 1, 1): 1,
            (3, 2, 1): 1,
            (3, 1, 0): 0,
            (3, 6, 2): 1,
            (3, 5, 2): 1,
            (3, 6, 0): 0,
            (3, 5, 1): 1,
            (3, 6, 1): 1,
            (2, 1, 0): 0,
            (3, 5, 0): 0,
            (2, 1, 1): 0,
            (2, 0, 0): 0,
            (3, 0, 0): 0,
            (3, 9, 2): 0,
            (3, 0, 1): 1,
            (3, 9, 1): 0,
        }
        assert auts == target_auts

    def test_list_orbits(self):
        nets, invs = graphlets.graphlets(
            n=3,
            layers=["a", "b", "c"],
            n_l=2,
            couplings="categorical",
            allowed_aspects="all",
        )
        auts = graphlets.automorphism_orbits(nets, allowed_aspects="all")
        orbit_lists = graphlets.list_orbits(auts)
        target_orbit_lists = {
            2: [(2, 0, 0), (2, 1, 0)],
            3: [
                (3, 0, 1),
                (3, 9, 0),
                (3, 4, 0),
                (3, 3, 0),
                (3, 4, 1),
                (3, 8, 0),
                (3, 7, 0),
                (3, 8, 1),
                (3, 2, 2),
                (3, 1, 1),
                (3, 2, 0),
                (3, 7, 2),
                (3, 2, 1),
                (3, 1, 0),
                (3, 6, 1),
                (3, 5, 1),
                (3, 6, 0),
                (3, 5, 0),
                (3, 0, 0),
            ],
        }
        assert set(orbit_lists[2]) == set(target_orbit_lists[2])
        assert set(orbit_lists[3]) == set(target_orbit_lists[3])

    def test_orbit_equations(self):
        nets, invs = graphlets.graphlets(
            n=3,
            layers=["a", "b", "c"],
            n_l=2,
            couplings="categorical",
            allowed_aspects="all",
        )
        auts = graphlets.automorphism_orbits(nets, allowed_aspects="all")
        orbit_eqs = graphlets.orbit_equations(
            n=3, nets=nets, auts=auts, invs=invs, allowed_aspects="all"
        )
        target_orbit_eqs = {
            (((2, 1, 0), 1), ((2, 0, 0), 1)): {
                (3, 2, 0): 1,
                (3, 5, 1): 1,
                (3, 6, 1): 1,
                (3, 7, 0): 1,
            },
            ((2, 0, 0), 2): {
                (3, 5, 0): 1,
                (3, 1, 0): 1,
                (3, 4, 0): 1,
                (3, 0, 0): 1,
                (3, 4, 1): 1,
                (3, 3, 0): 1,
                (3, 6, 0): 1,
            },
            ((2, 1, 0), 2): {(3, 8, 0): 1, (3, 7, 2): 1, (3, 9, 0): 1},
        }
        assert orbit_eqs == target_orbit_eqs
        # test with 4 nodes
        nets, invs = graphlets.graphlets(
            n=4,
            layers=["a", "b", "c"],
            n_l=2,
            couplings="categorical",
            allowed_aspects="all",
        )
        auts = graphlets.automorphism_orbits(nets, allowed_aspects="all")
        orbit_eqs = graphlets.orbit_equations(
            n=4, nets=nets, auts=auts, invs=invs, allowed_aspects="all"
        )

    ### tests for independent_equations file

    def test_independent_equations(self):
        inds, eqs = graphlets.independent_equations(
            n=3, n_l=2, layers=["a", "b", "c"], allowed_aspects="all"
        )
        target_inds = set(
            [((2, 0, 0), 2), (((2, 1, 0), 1), ((2, 0, 0), 1)), ((2, 1, 0), 2)]
        )
        target_eqs = {
            (((2, 1, 0), 1), ((2, 0, 0), 1)): {
                (3, 2, 0): 1,
                (3, 5, 1): 1,
                (3, 6, 1): 1,
                (3, 7, 0): 1,
            },
            ((2, 0, 0), 2): {
                (3, 5, 0): 1,
                (3, 1, 0): 1,
                (3, 4, 0): 1,
                (3, 0, 0): 1,
                (3, 4, 1): 1,
                (3, 3, 0): 1,
                (3, 6, 0): 1,
            },
            ((2, 1, 0), 2): {(3, 8, 0): 1, (3, 7, 2): 1, (3, 9, 0): 1},
        }
        assert inds == target_inds
        assert eqs == target_eqs

    def test_redundant_orbits(self):
        nets, invs = graphlets.graphlets(
            n=3,
            layers=["a", "b", "c"],
            n_l=2,
            couplings="categorical",
            allowed_aspects="all",
        )
        auts = graphlets.automorphism_orbits(nets, allowed_aspects="all")
        inds, eqs = graphlets.independent_equations(
            n=3, n_l=2, layers=["a", "b", "c"], allowed_aspects="all"
        )
        orbit_is = graphlets.orbit_numbers(n=3, nets=nets, auts=auts)
        orbit_list = graphlets.ordered_orbit_list(orbit_is)
        reds = graphlets.redundant_orbits(inds, eqs, orbit_is, orbit_list)
        target_reds = ["(3, 7, 0)", "(3, 9, 0)", "(3, 6, 0)"]
        assert set(reds) == set(target_reds)


def makesuite():
    suite = unittest.TestSuite()
    suite.addTest(TestGraphlets("test_graphlets"))
    suite.addTest(TestGraphlets("test_automorphism_orbits"))
    suite.addTest(TestGraphlets("test_list_orbits"))
    suite.addTest(TestGraphlets("test_orbit_equations"))
    suite.addTest(TestGraphlets("test_independent_equations"))
    suite.addTest(TestGraphlets("test_redundant_orbits"))
    return suite


def test_graphlets(**kwargs):
    suite = makesuite(**kwargs)
    return unittest.TextTestRunner().run(suite).wasSuccessful()


if __name__ == "__main__":
    sys.exit(not test_graphlets())
