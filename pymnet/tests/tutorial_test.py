import subprocess
import sys
import unittest

import nbformat


class TestTutorials(unittest.TestCase):
    def setUp(self):
        self.networktypes = "../../doc/tutorials/networktypes"

    def test_networktypes(self):
        subprocess.call(
            f"jupyter nbconvert --to notebook --execute {self.networktypes}.ipynb",
            shell=True,
        )
        nb = nbformat.read(f"{self.networktypes}.nbconvert.ipynb", as_version=4)
        nb_original = nbformat.read(f"{self.networktypes}.ipynb", as_version=4)
        out = [c["outputs"] for c in nb.cells if c["cell_type"] == "code"]
        out_original = [
            c["outputs"] for c in nb_original.cells if c["cell_type"] == "code"
        ]
        self.assertListEqual(out, out_original)

    def tearDown(self):
        subprocess.call(
            f"rm ../../doc/tutorials/{self.networktypes}.nbconvert.ipynb", shell=True
        )


def test_tutorials():
    suite = unittest.TestSuite()
    suite.addTest(TestTutorials("test_networktypes"))


if __name__ == "__main__":
    sys.exit(not test_tutorials())
