"""Multilayer network isomorphism backend using PyBliss. 

You can download PyBliss here:
http://www.tcs.hut.fi/Software/bliss/
"""

import PyBliss as bliss
from . import isomcore


class AuxiliaryGraphBuilderBliss(isomcore.AuxiliaryGraphBuilder):
    has_comparison=True
    has_complete_invariant=True
    has_automorphism_group_generators=True
    has_isomorphism_mapping=True
    
    def build_init(self):
        self.blissgraph=bliss.Graph()

    def add_node(self,name,color):
        self.blissgraph.add_vertex(name,color=color)

    def add_link(self,node1,node2):
        self.blissgraph.add_edge(node1,node2)

    def compare_structure(self,other):
        return self.blissgraph.get_isomorphism(other.blissgraph)!=None

    def complete_invariant_structure(self):
        return str(self.blissgraph.relabel(self.blissgraph.canonical_labeling()))

    def finalize(self):
        pass

    def _automorphism_generators(self):
        perms=[]
        def updater(val1,val2):
            perms.append(val1)

        self.blissgraph.find_automorphisms(updater)
    
        return perms

    def _isomorphism_mapping(self,other):
        return self.blissgraph.get_isomorphism(other.blissgraph)
