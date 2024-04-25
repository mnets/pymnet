"""Multilayer network isomorphism backend using Bliss through bliss_bind."""

import bliss_bind as bb
from . import isomcore


class AuxiliaryGraphBuilderBlissBind(isomcore.AuxiliaryGraphBuilder):
    has_comparison = True
    has_complete_invariant = True
    has_automorphism_group_generators = True
    has_isomorphism_mapping = True

    def __init__(self, net, allowed_aspects="all", reduction_type="auto"):
        super().__init__(net, allowed_aspects, reduction_type)
        self.node_name = {}
        self.node_index = {}
        self.neighbours = {}
        self.bbgraph = bb.Graph()

    def build_init(self):
        pass

    def add_node(self, name, color):
        if name in self.node_index:
            raise ValueError(f"Node with name {name} already exists")
        v = self.bbgraph.add_vertex(color=color)
        self.node_name[v] = name
        self.node_index[name] = v
        self.neighbours[v] = set()

    def get_isomorphism(self, other):
        if self.node_name.keys() != other.node_name.keys():
            return None

        self_degs = [len(self.neighbours[v])
                     for v in self.node_name]
        other_degs = [len(other.neighbours[v])
                      for v in other.node_name]
        if sorted(self_degs) != sorted(other_degs):
            return None

    def add_link(self, node1, node2):
        self.bbgraph.add_edge(self.node_index[node1],
                              self.node_index[node2])
        self.neighbours[node1].append(node2)
        self.neighbours[node2].append(node1)

    def compare_structure(self, other):
        # return self.bbgraph.get_isomorphism(other.bbgraph) is not None
        raise NotImplementedError("This method is not implemented")

    def complete_invariant_structure(self):
        return str(self.bbgraph.relabel(
            self.bbgraph.canonical_form()))

    def finalize(self):
        pass

    def _automorphism_generators(self):
        perms = []
        self.bbgraph.find_automorphisms(
                callback=lambda x: perms.append(x))

        return perms

    def _isomorphism_mapping(self, other):
        # return self.bbgraph.get_isomorphism(other.blissgraph)
        raise NotImplementedError("This method is not implemented")
