"""Multilayer network isomorphism backend using Bliss through bliss_bind."""

import bliss_bind

from . import isomcore


class AuxiliaryGraphBuilderBlissBind(isomcore.AuxiliaryGraphBuilder):
    has_comparison = True
    has_complete_invariant = True
    has_automorphism_group_generators = True
    has_isomorphism_mapping = True

    def build_init(self):
        self.bbgraph = bliss_bind.NamedGraph()

    def add_node(self, name, color):
        self.bbgraph.add_node(name, color)

    def add_link(self, node1, node2):
        self.bbgraph.add_link(node1, node2)

    def compare_structure(self, other):
        return self.bbgraph.get_isomorphism(other.bbgraph) is not None

    def complete_invariant_structure(self):
        return self.bbgraph.canonical_graph()

    def finalize(self):
        pass

    def _automorphism_generators(self):
        return self.bbgraph.find_automorphisms()

    def _isomorphism_mapping(self, other):
        return self.bbgraph.get_isomorphism(other.bbgraph)
