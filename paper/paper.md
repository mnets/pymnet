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

Many complex systems can be readily modeled as networks and represented as graphs. 
Such systems include social interactions, transport infrastructures, biological pathways, brains, ecosystems, and many more. 
A major advantage of representing complex systems as graphs is that the same graph tools and methods can be applied in a wide variety of domains. 
However, the graph representation has its limitations. 
For many systems, there is a need to represent richer network data, such as multidimensional features, several types of interactions, numerous layers of hierarchy, and multiple modalities, to capture the structure and dynamics of the systems more accurately than simple graphs would allow. 
Multilayer networks generalize graphs to capture the rich network data often associated with complex systems, allowing us to study a broad range of phenomena using a common representation, using the same multilayer tools and methods. 
With `pymnet`, we introduce a Python package that provides the essential data structures and computational tools for multilayer network analysis.

# Statement of Need

`pymnet` is a Python package for creating, analyzing, and visualizing multilayer networks. 
It is designed for network scientists with an easy-to-use yet flexible interface, featuring, inter alia, representations of a very general class of multilayer networks, structural metrics of multilayer networks (e.g., clustering coefficients and graphlet analysis), multilayer-network transforms, multilayer-network isomorphisms and automorphisms (with [PyBliss](http://www.tcs.hut.fi/Software/bliss/) [@junttila2011], [@junttila2007]), and random multilayer-network models.

Different kinds of multilayer network data are becoming more and more available, but our computational tools for handling such data are lagging behind. 
Python is a popular programming language for network scientists and data scientists, and `pymnet` addresses the need for a feature-rich multilayer-network package in the language.

`pymnet` implements the general multilayer-network framework described by @kivela2014. 
The *multilayer network* $M$ is defined by 
$$M = (V_M, E_M, V, \mathbf{L})\;,$$
where the sequence $\mathbf{L} = \( L_a \)_{a=1}^{d}$ defines sets $L_a$ of *elementary layers*, the set $V$ defines the *nodes* of the network, the vertices (that can be connected by edges) of the network are *node-layers* $V_M \subseteq{V \times L_1 \times ... \times L_d}$, and *edges* $E_M \subseteq V_M \times V_M$ are defined between node-layers. 
Put simply, a node-layer is an association of a node $v \in V$ with a layer $\in L_1 \times ... \times L_d$ with dimensionality $d$, nodes can exist on an arbitrary number of layers, and edges can connect node-layers within layers and across arbitrary pairs of layers, which can differ in an arbitrary number of dimensions. 
The dimensions $1,2,...,d$ are called the aspects of the network.

Beyond the general multilayer-network framework described by @kivela2014, `pymnet` also includes a specialized implementation of multiplex networks, a common subtype of multilayer networks. 
In multiplex networks, edges across layers (interlayer edges) only occur between a node and its counterpart(s) on the other layers. 
The advantages of the specialization include, for example, automatic lazy evaluation of interlayer-coupling edges.

# Features and Examples

`pymnet` contains submodules for advanced structural analysis of multilayer networks. 
Graphlet-degree analysis is a successful tool for investigating the structure of graphs that has been generalized to multilayer networks [@sallmen2022], 
and `pymnet` implements graphlet-degree analysis for single-aspect multiplex networks. **TODO: we haven't defined "aspect"**
A graphlet is an isomorphism class of (connected) induced subgraphs that are typically small. 
`pymnet` can generate all graphlets of a specified size, i.e., all isomorphic multiplex networks with a user-specified number of nodes and layers (coming from a user-defined set of layers), user-defined interlayer couplings, and a user-defined type of multilayer isomorphism. 
From the graphlets, `pymnet` can compute the automorphism orbits of nodes or node-layers in the graphlets, with a user-specified type of isomorphism. 
For example, we can use `pymnet` to enumerate and visualize all automorphism orbits of nodes using node-layer isomorphism of single-aspect multiplex graphlets with two or three nodes and two layers. 
The results are depicted in \autoref{fig:automorphisms}. 

![Visualization script from the [repository](https://github.com/bolozna/multiplex-graphlet-analysis/blob/master/visualization.py) provided by @sallmen2022](https://github.com/mnets/pymnet/blob/publication/paper/figs/l2_n3.png?raw=true "Automorphism orbits of nodes with node-layer isomorphism"){label="fig:automorphisms"}

**TODO: do we want the code examples here? reconsider - perhaps we should rather have a demo that shows the data structures (before the computational demo)**

We can generate networks and calculate graphlet-degree distributions for them (using [interface](https://github.com/bolozna/multiplex-graphlet-analysis/blob/master/interface.py) from @sallmen2022):

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

From the orbit counts, we can calculate the graphlet correlation distance (GCD) [@yaverouglu2014] between the two networks:

```python
orbits_1 = interface.read_graphlet_degree_distribution_folder('Results/M_1_2')
orbits_2 = interface.read_graphlet_degree_distribution_folder('Results/M_2_2')
gcm_1 = pn.graphlets.GCM(orbits_1)
gcm_2 = pn.graphlets.GCM(orbits_2)
print(pn.graphlets.GCD(gcm_1,gcm_2))
```

outputs `5.999478380647439`.

# Related Software

`pymnet` extends the popular [networkx](https://networkx.org/) package developed for single-layer graph analysis such that (some) [networkx](https://networkx.org/) functions can be applied to the individual layers of a multilayer network. 
To solve multilayer-network isomorphisms, `pymnet` uses a backend package, which can be either [networkx](https://networkx.org/) (limited functionality) or [PyBliss](http://www.tcs.hut.fi/Software/bliss/) [@junttila2011; @junttila2007] (full functionality).

**TODO should we mention Reticula, hypernetx/hypergraphx, etc. as other examples of libraries enabling richer network analysis but with different foci?**

# Projects Using `pymnet`

Pymnet has been used in multiple scientific publications, for example @kivela2014, @kivela2017, @sallmen2022, and @nurmi2023.

# Acknowledgments

**TODO**

# References

