import math
import random
import sys
import unittest

from pymnet import diagnostics, models, net


class TestModels(unittest.TestCase):

    def setUp(self):
        pass

    def test_monoplex_erdosrenyi(self):
        size = 10
        full = net.MultilayerNetwork(aspects=0)
        models.single_layer_er(
            full, range(10, 10 + size), p=None, edges=(size * (size - 1)) // 2
        )
        for i in full:
            for j in full:
                if i != j:
                    self.assertEqual(full[i, j], 1)
        self.assertEqual(len(full.edges), int((size * (size - 1)) / 2))

        net2 = net.MultilayerNetwork(aspects=0)
        models.single_layer_er(net2, range(10), p=None, edges=30)
        self.assertEqual(len(net2.edges), 30)

        net3 = net.MultilayerNetwork(aspects=0)
        models.single_layer_er(net3, range(10), p=1.0, edges=None)
        self.assertEqual(len(net3.edges), 45)

    def test_multiplex_erdosrenyi(self):
        net = models.er(10, 0.5)
        net2 = models.er(10, [0.4, 0.6])

        # test that there are some links but not all
        self.assertTrue(1 < len(list(net.edges)) < 10 * 9 / 2.0)
        self.assertTrue(1 < len(list(net2.A[1].edges)) < 10 * 9 + 10)

        net3 = models.er(10, edges=[30, 45])
        self.assertEqual(len(net3.A[0].edges), 30)
        self.assertEqual(len(net3.A[1].edges), 45)

        net4 = models.er([range(10), range(5, 15)], edges=[30, 45])
        self.assertEqual(len(net4.A[0].edges), 30)
        self.assertEqual(len(net4.A[1].edges), 45)
        self.assertEqual(set(net4.A[0]), set(range(10)))
        self.assertEqual(set(net4.A[1]), set(range(5, 15)))

        net5 = models.er([range(10), range(5, 15)], edges=30)
        self.assertEqual(len(net5.A[0].edges), 30)
        self.assertEqual(len(net5.A[1].edges), 30)
        self.assertEqual(set(net5.A[0]), set(range(10)))
        self.assertEqual(set(net5.A[1]), set(range(5, 15)))

    def test_monoplex_configuration_model(self):
        net = models.conf({5: 1000})  # maxdeg << sqrt(number of nodes)
        self.assertEqual(diagnostics.degs(net), {5: 1000})

        net = models.conf({50: 100})
        self.assertEqual(diagnostics.degs(net), {50: 100})

        # zero degrees
        net = models.conf({50: 100, 0: 10})
        self.assertEqual(diagnostics.degs(net), {50: 100, 0: 10})

        net = models.conf(
            dict(map(lambda x: (x, int(math.sqrt(x) + 1)), range(101))),
            degstype="nodes",
        )
        for i in range(101):
            self.assertEqual(net[i].deg(), int(math.sqrt(i) + 1))

        # zero degrees
        net = models.conf(
            dict(map(lambda x: (x, int(math.sqrt(x))), range(99))), degstype="nodes"
        )
        for i in range(99):
            self.assertEqual(net[i].deg(), int(math.sqrt(i)))

        net = models.conf(net)
        for i in range(99):
            self.assertEqual(net[i].deg(), int(math.sqrt(i)))

    def test_multiplex_configuration_model(self):
        net = models.conf([{50: 100}, {50: 100}])
        self.assertEqual(diagnostics.multiplex_degs(net), {0: {50: 100}, 1: {50: 100}})

        net = models.conf({"l1": {50: 100}, "l2": {50: 100}})
        self.assertEqual(
            diagnostics.multiplex_degs(net), {"l1": {50: 100}, "l2": {50: 100}}
        )

        net = models.conf(net)
        self.assertEqual(
            diagnostics.multiplex_degs(net), {"l1": {50: 100}, "l2": {50: 100}}
        )

        degs = {
            "l1": dict(map(lambda x: (x, 2 * int(math.sqrt(x))), range(100))),
            "l2": dict(map(lambda x: (x, 2 * int(math.sqrt(x))), range(20, 120))),
        }
        net = models.conf(degs, degstype="nodes")
        self.assertEqual(diagnostics.multiplex_degs(net, degstype="nodes"), degs)
        self.assertEqual(set(net.A["l1"]), set(range(100)))
        self.assertEqual(set(net.A["l2"]), set(range(20, 120)))

    def test_full_multiplex_network(self):
        self.assertEqual(diagnostics.degs(models.full(nodes=10, layers=None)), {9: 10})

        self.assertEqual(
            diagnostics.degs(models.full(nodes=10, layers=["a", "b"])), {10: 20}
        )
        self.assertEqual(
            diagnostics.multiplex_degs(models.full(nodes=10, layers=["a", "b"])),
            {"a": {9: 10}, "b": {9: 10}},
        )

        self.assertEqual(diagnostics.degs(models.full(nodes=10, layers=2)), {10: 20})
        self.assertEqual(
            diagnostics.multiplex_degs(models.full(nodes=10, layers=2)),
            {0: {9: 10}, 1: {9: 10}},
        )

    def test_er_partially_interconnected(self):
        random.seed(42)
        nodes = [list(range(10)), list(range(0, 10, 2))]
        ps = [0.1, 0.1]
        model = models.er_partially_interconnected(
            nodes, ps, couplings=("categorical", 0.9)
        )
        self.assertListEqual(
            list(model.edges)[:2], [(0, 5, 0, 0, 1), (0, 0, 0, 1, 0.9)]
        )

    def test_conf_overlaps(self):
        ol_dict = {
            (0, 0): {0: 0, 1: 0, 2: 1, 3: 1},
            (0, 1): {0: 1, 1: 1, 2: 0},
            (1, 1): {0: 0, 1: 0, 4: 1, 5: 1},
        }
        model = models.conf_overlaps(ol_dict)
        self.assertListEqual(
            list(model.edges),
            [(0, 1, 0, 0, 1), (0, 1, 1, 1, 1), (2, 3, 0, 0, 1), (4, 5, 1, 1, 1)],
        )
        ol_dict = {
            (0, 0): {0: 1, 1: 0, 2: 1, 3: 2},
            (0, 1): {0: 1, 1: 1, 2: 0},
            (1, 1): {0: 0, 1: 1, 4: 2, 5: 1},
        }
        random.seed(1)
        model = models.conf_overlaps(ol_dict)
        self.assertSetEqual(
            set(model.edges),
            {
                (0, 1, 0, 0, 1),
                (0, 1, 1, 1, 1),
                (0, 3, 0, 0, 1),
                (1, 4, 1, 1, 1),
                (2, 3, 0, 0, 1),
                (4, 5, 1, 1, 1),
            },
        )

    def test_ba_total_degree(self):
        random.seed(42)
        model = models.ba_total_degree(100, [1, 2])
        self.assertEqual(len(list(model.edges)), 295)
        self.assertListEqual(
            list(model.edges)[10:12], [(0, 12, 1, 1, 1), (0, 22, 1, 1, 1)]
        )

    # TODO double-check model implementation
    def test_geo(self):
        random.seed(42)
        model = models.geo(200, [10, 10])
        self.assertEqual(len(list(model.edges)), 26)
        self.assertListEqual(
            list(model.edges)[:2], [(2, 90, 0, 0, 1), (2, 186, 0, 0, 1)]
        )

    def test_ws(self):
        random.seed(42)
        model = models.ws(10, [20, 20])
        self.assertEqual(len(list(model.edges)), 40)
        self.assertListEqual(
            list(model.edges)[10:12], [(1, 9, 0, 0, 1), (1, 4, 0, 0, 1)]
        )

    # TODO double-check model implementation
    def test_er_overlaps_match_aggregated(self):
        pass


def test_models():
    suite = unittest.TestSuite()
    suite.addTest(TestModels("test_monoplex_erdosrenyi"))
    suite.addTest(TestModels("test_multiplex_erdosrenyi"))
    suite.addTest(TestModels("test_monoplex_configuration_model"))
    suite.addTest(TestModels("test_multiplex_configuration_model"))
    suite.addTest(TestModels("test_full_multiplex_network"))
    suite.addTest(TestModels("test_er_partially_interconnected"))
    suite.addTest(TestModels("test_conf_overlaps"))
    suite.addTest(TestModels("test_ba_total_degree"))
    suite.addTest(TestModels("test_geo"))
    suite.addTest(TestModels("test_ws"))
    suite.addTest(TestModels("test_er_overlaps_match_aggregated"))

    return unittest.TextTestRunner().run(suite).wasSuccessful()


if __name__ == "__main__":
    sys.exit(not test_models())
