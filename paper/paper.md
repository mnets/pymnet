---
title: 'Pymnet: A Multilayer Networks Library for Python'
tags:
- Python
- multilayer network
- multiplex network
- network science
- attributed graph
authors:
- name: Arash Badie-Modiri
  orcid: 0000-0002-2027-360X
  affiliation: "1"
- name: Corinna Coupette
  orcid: 0000-0001-9151-2092
  affiliation: "2,3"
- name: Tarmo Nurmi
  orcid: 0000-0003-0258-7776
  affiliation: "4"
- name: Mikko Kivelä
  orcid: 0000-0003-2049-1954
  affiliation: "4" 
affiliations:
- name: Central European University, Vienna, Austria
  index: 1
- name: KTH Royal Institute of Technology, Stockholm, Sweden
  index: 2
- name: Max Planck Institute for Informatics, Saarbrücken, Germany
  index: 3
- name: Aalto University, Helsinki, Finland
  index: 4
  
date: 14 May 2024
bibliography: paper.bib
 
---

# Summary

Many complex systems with interacting elements can be represented in a natural way as graphs. Such systems include social networks, transportation systems, interacting and regulatory chemical pathways in cells, brain function, societal systems, ecological networks, co-authorship patterns, and many more. A major advantage of representing such systems as graphs is that the same graph tools and methods can be applied in a wide variety of domains. However, the graph representation has its limitations. For many systems, there is a need to represent more rich network data, such as networks with multidimensional data, several types of interactions, layers of hierarchy, and multiple modalities, to more accurately capture the structure and behavior of the systems in a way that simple-form graphs cannot do. One generalization of graphs that can capture the aforementioned rich network data is multilayer networks [@kivela2014]. Multilayer networks can capture a wide variety of phenomena using a common representation. Just like graphs, this means that the same multilayer tools and techniques can be applied across vastly different domains. Pymnet provides the data structures and computational tools for multilayer network analysis in one Python package.

# Statement of Need

Pymnet is a Python package for creating, analyzing, and visualizing multilayer networks. It is designed for network scientists with an easy-to-use yet flexible interface, and features representation of a very general class of multilayer networks, structural metrics of multilayer networks (e.g. clustering coefficients, graphlet analysis), multilayer network transforms, multilayer networks isomorphisms and automorphisms (with [PyBliss](http://www.tcs.hut.fi/Software/bliss/) [@junttila2011], [@junttila2007]), and multilayer random network models, among other things.

Different kinds of multilayered and multimodal network data are becoming more and more available, but programmatic tools for handling such data are not mature. Python is a popular programming language for network scientists and data scientists, and pymnet answers the need for a featured multilayer network package available for the language.

Pymnet implements the general multilayer network framework described in [@kivela2014]. The multilayer network $M$ is defined by
$$M = (V_M, E_M, V, \mathbf{L})$$
where the sequence $\mathbf{L} = \( L_a \)_{a=1}^{d}$ defines sets $L_a$ of elementary layers, the set $V$ defines the nodes of the network, the vertices (that can be connected by edges) of the network are node-layers $V_M \subseteq{V \times L_1 \times ... \times L_d}$, and edges $E_M \subseteq V_M \times V_M$ are defined between node-layers. Simply, a node-layer is an association of a node $\in V$ with a layer $\in L_1 \times ... \times L_d$ with dimensionality $d$, and nodes can exist on an arbitrary number of layers and edges can connect node-layers within layers and across arbitrary layer pairs which can vary in an arbitrary number of dimensions. The dimensions $1,2,...,d$ are called the aspects of the network.

Pymnet also includes a specialized implementation of multiplex networks, a common subtype of multilayer networks. In multiplex networks, edges across layers (interlayer edges) only occur between a node and its counterpart(s) on the other layers. The advantages of the specialization include, for example, automatic lazy evaluation of interlayer coupling edges.

# Features and examples

Pymnet contains submodules for advanced structural analysis of multilayer networks. Graphlet degree analysis is a successful tool in the investigation of structure of graphs, and it has been generalized to multilayer networks [@sallmen2022]. Pymnet implements the graphlet degree analysis tools for single-aspect multiplex networks. A graphlet is an isomorphism class of (connected) networks which are typically small. Pymnet can generate all graphlets of specified size, i.e. all isomorphic multiplex networks with a user-specified number of nodes and layers (coming from a user-defined set of layers), user-defined interlayer couplings, and user-defined type of multilayer isomorphism. From the graphlets, pymnet can compute the automorphism orbits of nodes or node-layers in the graphlets, with user-specified type of isomorphism. For example, we can use pymnet to number and visualize all automorphism orbits of nodes using node-layer isomorphism of single-aspect multiplex graphlets with two or three nodes and two layers:

![3 nodes, 2 layers automorphism orbits](https://github.com/mnets/pymnet/blob/publication/paper/figs/l2_n3.png?raw=true "Automorphism orbits of nodes with node-layer isomorphism")

_Visualization script from [@sallmen2022] [repository](https://github.com/bolozna/multiplex-graphlet-analysis/blob/master/visualization.py)._

We can generate networks and calculate graphlet degree distributions for them (using [interface](https://github.com/bolozna/multiplex-graphlet-analysis/blob/master/interface.py) from [@sallmen2022]):

```python
import pymnet as pn
import interface

def make_example_network_1():
    M = pn.MultiplexNetwork(couplings='categorical',fullyInterconnected=True)
    M[0,1,'a','a'] = 1
    M[0,2,'b','b'] = 1
    return M

def make_example_network_2():
    M = pn.MultiplexNetwork(couplings='categorical',fullyInterconnected=True)
    M['alice','bob','a','a'] = 1
    M['bob','carol','a','a'] = 1
    M['alice','carol','a','a'] = 1
    M['alice','carol','b','b'] = 1
    return M

M_1 = make_example_network_1()
M_2 = make_example_network_2()
interface.graphlet_degree_distributions(M_1,3,2,save_name='M_1')
interface.graphlet_degree_distributions(M_2,3,2,save_name='M_2')
```

This produces files `Results/M_1_2/M_1_a_b.txt` with content

n|(2, 0, 0)|(2, 1, 0)|(3, 0, 0)|(3, 0, 1)|(3, 1, 0)|(3, 1, 1)|(3, 2, 0)|(3, 2, 1)|(3, 2, 2)|(3, 3, 0)|(3, 4, 0)|(3, 4, 1)|(3, 5, 0)|(3, 5, 1)|(3, 6, 0)|(3, 6, 1)|(3, 7, 0)|(3, 7, 2)|(3, 8, 0)|(3, 8, 1)|(3, 9, 0)
:-:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:
0|2|0|0|0|1|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0
1|1|0|0|0|0|1|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0
2|1|0|0|0|0|1|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0

and `Results/M_2_2/M_2_a_b.txt` with content

n|(2, 0, 0)|(2, 1, 0)|(3, 0, 0)|(3, 0, 1)|(3, 1, 0)|(3, 1, 1)|(3, 2, 0)|(3, 2, 1)|(3, 2, 2)|(3, 3, 0)|(3, 4, 0)|(3, 4, 1)|(3, 5, 0)|(3, 5, 1)|(3, 6, 0)|(3, 6, 1)|(3, 7, 0)|(3, 7, 2)|(3, 8, 0)|(3, 8, 1)|(3, 9, 0)
:-:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:
carol|1|1|0|0|0|0|0|0|0|0|0|0|0|1|0|0|0|0|0|0|0
bob|2|0|0|0|0|0|0|0|0|0|0|0|1|0|0|0|0|0|0|0|0
alice|1|1|0|0|0|0|0|0|0|0|0|0|0|1|0|0|0|0|0|0|0

where `(2,0,0)`, `(2,1,0)` etc. are representations of the orbits.

From the orbit counts, we can calculate the graphlet correlation distance (GCD) between the two networks:

```python
orbits_1 = interface.read_graphlet_degree_distribution_folder('Results/M_1_2')
orbits_2 = interface.read_graphlet_degree_distribution_folder('Results/M_2_2')
gcm_1 = pn.graphlets.GCM(orbits_1)
gcm_2 = pn.graphlets.GCM(orbits_2)
print(pn.graphlets.GCD(gcm_1,gcm_2))
```

outputs `5.99947838065`.

# Related Software

Pymnet extends the popular [networkx](https://networkx.org/) package—used for single-layer graph analysis—such that (some) [networkx](https://networkx.org/) functions can be applied to the individual layers of a multilayer network. To solve multilayer network isomorphisms, pymnet uses a back-end package, which can be either [networkx](https://networkx.org/) (limited functionality) or [PyBliss](http://www.tcs.hut.fi/Software/bliss/) [@junttila2011], [@junttila2007] (full functionality).

# Projects Using Pymnet

Pymnet has been used in multiple scientific publications, for example [@kivela2014], [@kivela2017], [@sallmen2022], and [@nurmi2023].

# Acknowledgments

# References

