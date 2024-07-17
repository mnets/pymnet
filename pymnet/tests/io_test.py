import os
import sys
import tempfile
import unittest
from operator import itemgetter

from pymnet import net, netio


class TestIO(unittest.TestCase):

    def setUp(self):
        pass

    def test_read_ucinet_flat_fullnet(self):
        netfile = """DL N = 5
Data:
0 1 1 1 1
1 0 1 0 0
1 1 0 0 1
1 0 0 0 0
1 0 1 0 0"""
        net = netio.read_ucinet(netfile.split("\n"))
        self.assertEqual(net.aspects, 0)
        self.assertEqual(set(net), set([0, 1, 2, 3, 4]))
        self.assertEqual(set(net[0]), set([1, 2, 3, 4]))
        self.assertEqual(set(net[1]), set([0, 2]))
        self.assertEqual(set(net[2]), set([0, 1, 4]))
        self.assertEqual(set(net[3]), set([0]))
        self.assertEqual(set(net[4]), set([0, 2]))

        def test_labeled(netfile):
            net = netio.read_ucinet(netfile.split("\n"))
            self.assertEqual(net.aspects, 0)
            self.assertEqual(set(net), set(["barry", "david", "lin", "pat", "russ"]))
            self.assertEqual(set(net["barry"]), set(["david", "lin", "pat"]))
            self.assertEqual(set(net["david"]), set(["barry", "russ"]))
            self.assertEqual(set(net["lin"]), set(["barry", "pat"]))
            self.assertEqual(set(net["pat"]), set(["barry", "lin", "russ"]))
            self.assertEqual(set(net["russ"]), set(["david", "pat"]))

        netfile1 = """dl n=5
format = fullmatrix
labels:
barry,david,lin,pat,russ
data:
0 1 1 1 0
1 0 0 0 1
1 0 0 1 0
1 0 1 0 1
0 1 0 1 0"""
        test_labeled(netfile1)

        netfile2 = """dl n=5
format = fullmatrix
labels:
barry,david
lin,pat
russ
data:
0 1 1 1 0
1 0 0 0 1
1 0 0 1 0
1 0 1 0 1
0 1 0 1 0"""
        test_labeled(netfile2)

        netfile3 = """dl n=5
format = fullmatrix
labels embedded
data:
barry david lin pat russ
Barry 0 1 1 1 0
david 1 0 0 0 1
Lin 1 0 0 1 0
Pat 1 0 1 0 1
Russ 0 1 0 1 0"""
        test_labeled(netfile3)

    def test_read_ucinet_mplex_fullnet(self):
        netfile = """DL N = 5 nm=2
Data:
0 1 1 1 1
1 0 1 0 0
1 1 0 0 1
1 0 0 0 0
1 0 1 0 0
0 1 1 1 0
1 0 0 0 1
1 0 0 1 0
1 0 1 0 1
0 1 0 1 0"""
        net = netio.read_ucinet(netfile.split("\n"))
        self.assertEqual(net.aspects, 1)
        self.assertEqual(set(net), set([0, 1, 2, 3, 4]))
        self.assertEqual(set(net.A[0][0]), set([1, 2, 3, 4]))
        self.assertEqual(set(net.A[0][1]), set([0, 2]))
        self.assertEqual(set(net.A[0][2]), set([0, 1, 4]))
        self.assertEqual(set(net.A[0][3]), set([0]))
        self.assertEqual(set(net.A[0][4]), set([0, 2]))
        self.assertEqual(set(net.A[1][0]), set([1, 2, 3]))
        self.assertEqual(set(net.A[1][1]), set([0, 4]))
        self.assertEqual(set(net.A[1][2]), set([0, 3]))
        self.assertEqual(set(net.A[1][3]), set([0, 2, 4]))
        self.assertEqual(set(net.A[1][4]), set([1, 3]))

    def test_read_ucinet_mplex_nonglobalnodes(self):
        netfile = """DL N = 3 nm =2
Data:
0 1 1
1 0 1
1 1 0
0 0 0
0 0 1
0 1 0"""
        net = netio.read_ucinet(netfile.split("\n"), fullyInterconnected=False)
        self.assertEqual(set(net[0, 0]), set([(1, 0), (2, 0)]))
        self.assertEqual(set(net[1, 0]), set([(0, 0), (2, 0), (1, 1)]))
        self.assertEqual(set(net[2, 0]), set([(0, 0), (1, 0), (2, 1)]))
        self.assertEqual(set(net[0, 1]), set([]))
        self.assertEqual(set(net[1, 1]), set([(2, 1), (1, 0)]))
        self.assertEqual(set(net[2, 1]), set([(1, 1), (2, 0)]))

    def test_pickle(self):
        import pickle

        n = net.MultilayerNetwork(aspects=1)
        n[1, 2, 3, 4] = 1
        self.assertEqual(pickle.loads(pickle.dumps(n)), n)
        n = net.MultilayerNetwork(aspects=1, directed=True)
        n[1, 2, 3, 4] = 1
        self.assertEqual(pickle.loads(pickle.dumps(n)), n)

        n = net.MultiplexNetwork(couplings=[("categorical", 1)])
        n[1, 2, 3, 3] = 1
        self.assertEqual(pickle.loads(pickle.dumps(n)), n)
        n = net.MultiplexNetwork(couplings=[("categorical", 1)], directed=True)
        n[1, 2, 3, 3] = 1
        self.assertEqual(pickle.loads(pickle.dumps(n)), n)

    def test_write_json(self):
        import json

        n = net.MultiplexNetwork(couplings=[("categorical", 1)])
        n[1, 2, 3, 3] = 1
        j = json.loads(netio.write_json(n))
        self.assertEqual({node["name"] for node in j["nodes"]}, {1, 2})
        self.assertEqual({layer["name"] for layer in j["layers"]}, {3})
        self.assertEqual(
            [
                ({link["source"], link["target"]}, link["value"], link["layer"])
                for link in j["links"]
            ],
            [({0, 1}, 1, 0)],
        )

        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "fobject"), "w") as f:
                netio.write_json(n, outputfile=f)
            with open(os.path.join(tmp, "fobject")) as f:
                self.assertEqual(json.load(f), j)

            netio.write_json(n, outputfile=os.path.join(tmp, "fname"))
            with open(os.path.join(tmp, "fname")) as f:
                self.assertEqual(json.load(f), j)

    def test_write_edge_files(self):
        n = net.MultiplexNetwork(couplings=[("categorical", 1)])
        n[1, 2, 3, 3] = 1
        with tempfile.TemporaryDirectory() as tmp:
            name = os.path.join(tmp, "test")
            netio.write_edge_files(n, name, masterFile=True)

            with open(name + ".txt") as master:
                self.assertEqual(master.readlines(), ["test3.edg;3;\n"])

            with open(name + "3.edg") as layer:
                l1, l2, w = next(layer).split()
                self.assertEqual(({int(l1), int(l2)}, int(w)), ({1, 2}, 1))

    def test_read_edge_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            name = os.path.join(tmp, "test")
            fn = f"{name}.txt"
            with open(fn, "w") as f:
                f.write("1 1 2 0.5\n1 2 2 0.75")
            net = netio.read_edge_file(fn, sep=" ")
            self.assertEqual(len(net.edges), 1)
            with open(fn, "w") as f:
                f.write("1\t1\t2\t0.5\n1\t2\t2\t0.75")
            net = netio.read_edge_file(fn, sep="\t")
            self.assertEqual(len(net.edges), 1)

    def test_write_edge_file(self):
        n = net.MultiplexNetwork(couplings=[("categorical", 1)])
        n[1, 2, 3, 3] = 1
        with tempfile.TemporaryDirectory() as tmp:
            name = os.path.join(tmp, "test.edgelist")
            netio.write_edge_file(n, name, sep="\t")

            with open(name) as edges:
                layer, l1, l2, w = next(edges).split("\t")
                self.assertEqual(({int(l1), int(l2)}, int(w)), ({1, 2}, 1))
                self.assertEqual(int(layer), 3)
                net2 = netio.read_edge_file(name, sep="\t")
                self.assertListEqual(list(net2.edges), list(n.edges))


def test_io():
    suite = unittest.TestSuite()
    suite.addTest(TestIO("test_read_ucinet_flat_fullnet"))
    suite.addTest(TestIO("test_read_ucinet_mplex_fullnet"))
    suite.addTest(TestIO("test_read_ucinet_mplex_nonglobalnodes"))
    suite.addTest(TestIO("test_pickle"))
    suite.addTest(TestIO("test_write_json"))
    suite.addTest(TestIO("test_write_edge_files"))
    suite.addTest(TestIO("test_read_edge_file"))
    suite.addTest(TestIO("test_write_edge_file"))

    return unittest.TextTestRunner().run(suite).wasSuccessful()


if __name__ == "__main__":
    sys.exit(not test_io())
