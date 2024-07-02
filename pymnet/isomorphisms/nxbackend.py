import networkx
from networkx.algorithms import isomorphism as nxisomorphism

from . import isomcore


class AuxiliaryGraphBuilderNX(isomcore.AuxiliaryGraphBuilder):
    has_comparison = True
    has_isomorphism_mapping = True

    def build_init(self):
        self.nxgraph = networkx.Graph()

    def finalize(self):
        pass

    def add_node(self, name, color):
        self.nxgraph.add_node(name, color=color)

    def add_link(self, node1, node2):
        self.nxgraph.add_edge(node1, node2)

    def compare_structure(self, other):
        def matcher(n1, n2):
            return n1["color"] == n2["color"]

        return networkx.is_isomorphic(self.nxgraph, other.nxgraph, node_match=matcher)

    def _isomorphism_mapping(self, other):
        def matcher(n1, n2):
            return n1["color"] == n2["color"]

        m = nxisomorphism.GraphMatcher(self.nxgraph, other.nxgraph, node_match=matcher)
        # this needs to be run so that the mapping is created
        is_isomorphic = m.is_isomorphic()
        if is_isomorphic:
            return m.mapping
        else:
            return None
