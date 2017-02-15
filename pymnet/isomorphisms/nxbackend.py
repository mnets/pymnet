import networkx
import isomcore


class AuxiliaryGraphBuilderNX(isomcore.AuxiliaryGraphBuilder):
    has_comparison=True

    def build_init(self):
        self.nxgraph=networkx.Graph()

    def finalize(self):
        #print self.nodemap
        #print self.auxnodemap
        #print self.colormap
        #print self.auxcolormap
        pass

    def add_node(self,name,color):
        #print "Node: ",
        #print name,
        #print "color:",
        #print color
        self.nxgraph.add_node(name,color=color)

    def add_link(self,node1,node2):
        #print "Link:",
        #print node1,
        #print node2
        self.nxgraph.add_edge(node1,node2)

    def compare_structure(self,other):
        #matcher=networkx.algorithms.isomorphism.categorical_node_match("color",-1)
        matcher=lambda n1,n2:n1['color']==n2['color']
        return networkx.is_isomorphic(self.nxgraph,other.nxgraph,node_match=matcher)
        
