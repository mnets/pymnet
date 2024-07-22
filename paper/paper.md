---
title: 'pymnet: A Python Library for Multilayer Networks'
tags:
- Python
- multilayer network
- multiplex network
- network science
- attributed graph
authors:
- name: Tarmo Nurmi
  orcid: 0000-0003-0258-7776
  affiliation: "1"
- name: Arash Badie-Modiri
  orcid: 0000-0002-2027-360X
  affiliation: "2"
- name: Corinna Coupette
  orcid: 0000-0001-9151-2092
  affiliation: "1,3,4"
- name: Mikko Kivelä
  orcid: 0000-0003-2049-1954
  affiliation: "1" 
affiliations:
- name: Aalto University, Finland
  index: 1
- name: Central European University, Austria
  index: 2
- name: KTH Royal Institute of Technology, Sweden
  index: 3
- name: Max Planck Institute for Informatics, Germany
  index: 4
date: 19 June 2024
bibliography: paper.bib
 
---

# Summary

Many complex systems can be readily modeled as networks and represented as graphs. 
Such systems include social interactions, transport infrastructures, biological pathways, brains, ecosystems, and many more. 
A major advantage of representing complex systems as graphs is that the same graph tools and methods can be applied in a wide variety of domains. 
However, the graph representation has its limitations: 
many systems contain nodes with multidimensional features, interactions of various types, different levels of hierarchy, or multiple modalities, which deserve to be modeled but cannot be described by simple graphs.
Multilayer networks [@kivela2014] generalize graphs to capture the rich network data often associated with complex systems, allowing us to study a broad range of phenomena using the same representations, tools, and methods. 
With `pymnet`, we introduce a Python package that provides the essential data structures and computational tools for multilayer-network analysis.
As highlights, the library offers efficient and scalable implementations for sparse multilayer networks and multiplex networks, integration with `bliss` to analyze multilayer-network isomorphisms and automorphisms, and versatile methods for multilayer-network visualization.

# Statement of Need

[pymnet](https://github.com/mnets/pymnet) is a Python package for creating, analyzing, and visualizing multilayer networks. 
It is designed for network scientists with an easy-to-use yet flexible interface, featuring, inter alia, representations of a very general class of multilayer networks, structural metrics of multilayer networks (e.g., clustering coefficients [@cozzo2015structure] and graphlet analysis [@sallmen2022]), multilayer-network transforms, multilayer-network isomorphisms and automorphisms [@kivela2017] (with [`bliss`](https://users.aalto.fi/~tjunttil/bliss/) [@junttila2011; @junttila2007]), and random multilayer-network models.

Different kinds of multilayer network data are becoming increasingly available, but our computational tools for handling such data lag behind. 
Python is a popular programming language for network scientists and data scientists, and `pymnet` addresses the need for a feature-rich multilayer-networks package in the Python language that is actively maintained.

`pymnet` implements the general multilayer-network framework described by @kivela2014. 
A *multilayer network* $M$ is defined by $M = (V_M, E_M, V, \mathbf{L})$,
where the sequence $\mathbf{L} = (L_a)_{a=1}^{d}$ defines sets $L_a$ of *elementary layers*, the set $V$ defines the *nodes* of the network, the *node-layers* are $V_M \subseteq V \times L_1 \times ... \times L_d$, and the *edges* $E_M \subseteq V_M \times V_M$ are defined between node-layers. 
Put simply, a node-layer is an association of a node $v \in V$ with a layer $\in L_1 \times ... \times L_d$ of dimensionality $d$, nodes can exist on an arbitrary number of layers, and edges can connect node-layers within layers and across arbitrary pairs of layers, which can differ in an arbitrary number of dimensions. 
The dimensions $1,2,...,d$ are called the *aspects* of the network.

Beyond the general multilayer-network framework described by @kivela2014, `pymnet` also includes a specialized implementation of *multiplex* networks, a common subtype of multilayer networks. 
In multiplex networks, edges across layers (interlayer edges) only occur between a node and its counterpart(s) on the other layers. 
The advantages of this specialization include, for example, automatic lazy evaluation of interlayer-coupling edges.

# Main Features

`pymnet`'s main data structure is `MultilayerNetwork`, which is implemented as a dictionary of dictionaries with a tensor-like interface, where each key represents a node, and each value is another dictionary containing information about the neighbors of each node, with the neighbors as keys and the weights of their incident edges as values.
This structure ensures that adding nodes, removing nodes, querying for existence of edges, or querying for edge weights all have constant average time complexity, and iterating over the neighbors of a node is linear in the number of nodes. Furthermore, the memory requirements are in $O(|V| + |L| + |E|)$ and typically dominated by the number of edges in the network.

To represent multiplex networks, `pymnet` offers `MultiplexNetwork`, which exploits the special structure of interlayer edges for efficiency, storing intralayer edges separately for each layer and only generating interlayer edges according to the applicable interlayer-coupling rules when they are explicitly needed.
This ensures that we can always iterate over intralayer edges in linear time, and that interlayer edges only require constant memory (i.e., the memory to store the rule to generate them).

`pymnet` contains submodules for advanced analysis of multilayer networks.
One example is graphlet-degree analysis, a powerful tool for investigating the structure of graphs that has been generalized to multilayer networks [@sallmen2022] and is implemented in `pymnet` for single-aspect multiplex networks. 
A graphlet is an isomorphism class of (connected) induced subgraphs that are typically small. 
`pymnet` can generate all graphlets of a specified size, i.e., all isomorphic multiplex networks with a user-specified number of nodes and layers (coming from a user-defined set of layers), user-defined interlayer couplings, and a user-defined type of multilayer isomorphism. 
From the graphlets, `pymnet` can compute the automorphism orbits of nodes or node-layers in the graphlets, with a user-specified type of isomorphism. 
For example, we can use `pymnet` to enumerate and visualize all automorphism orbits of nodes in single-aspect multiplex graphlets with two or three nodes and two layers under node-layer isomorphism. 
The results are depicted in \autoref{fig:automorphisms}. 

Other amenities shipped with `pymnet` include graph generators for generalizations of popular random-graph models to multilayer networks (e.g., Erdős-Rényi models and configuration models) as well as utilities for multilayer-network visualization. 

![Using `pymnet` to enumerate and visualize automorphism orbits of nodes in single-aspect multiplex graphlets under node-layer isomorphism. [Visualization script](https://github.com/bolozna/multiplex-graphlet-analysis/blob/master/visualization.py) adapted from @sallmen2022. \label{fig:automorphisms}](https://github.com/mnets/pymnet/blob/publication/paper/figs/l2_n3.png?raw=true "Automorphism orbits of nodes with node-layer isomorphism"){ width=75% }

# Real-World Example

As an example of how `pymnet` can be used to analyze real-world data, we explore data documenting the *legal* international trade in endangered species, which is crucial for monitoring progress toward the United Nations' Sustainable Development Goal 15. 
The Convention on International Trade in Endangered Species of Wild Fauna and Flora (CITES) regulates this trade, and the [CITES database](https://trade.cites.org/) provides highly granular trade data, accompanied by great [documentation](https://trade.cites.org/cites_trade_guidelines/en-CITES_Trade_Database_Guide.pdf). 

To keep matters simple, we analyze an excerpt from the CITES database, investigating the trade in endangered species in two different *years* (2010 and 2020), for two different *trade terms* (live specimens and meat), and restricting ourselves to species taken from the *wild* and traded for *commercial* purposes.
In the multilayer-network model representing this data, our nodes are countries or territories importing and exporting endangered species (represented by their ISO-2 codes), our aspects are years (two elementary layers: 2010 and 2020) and trade terms (two elementary layers: "live" and "meat"), and our edges represent bilateral trades, measured in the number of specimens ("live") or the number of kilograms ("meat") traded. 
More details on the data provenance and our preprocessing steps are available in the `pymnet` repository.

In \autoref{fig:citestrade}, we visualize the data with `pymnet`, only drawing undirected edges representing aggregate trade volumes of at least one million specimens ("live") or one thousand kilograms ("meat"), scaling nodes by degree and highlighting OECD countries in red, as well as mapping trade volume to edge widths and edge colors.
Between 2010 and 2020, we observe roughly equal levels of trade in live specimens, but a pronounced increase in both trade volume and diversity of trade partners for trade in meat.

![Trade in live specimens (top) and meat (bottom) of endangered species in the years 2010 (left) and 2020 (right). \label{fig:citestrade}](https://github.com/mnets/pymnet/blob/publication/paper/figs/cites-trades_commercial_live-meat.png?raw=true "Trade in live specimens (top) and meat (bottom) of endangered species in the years 2010 (left) and 2020 (right)."){ width=95% } 

# Installation and Usage

Detailed installation and usage instructions, including tutorials demonstrating `pymnet`'s main functionality, can be found in the [pymnet documentation](https://mnets.github.io/pymnet/).

# Related Packages

`pymnet` extends the popular [networkx](https://networkx.org/) package developed for single-layer network analysis such that `networkx` functions can be applied to the individual layers of a multilayer network. These functions are automatically wrapped for use in `pymnet`, which has the benefit of automatically including new functionality added to `networkx`. 
To solve multilayer-network isomorphisms, `pymnet` uses a backend package, which can be either `networkx` (limited functionality) or [`bliss`](https://users.aalto.fi/~tjunttil/bliss/) [@junttila2011; @junttila2007] (full functionality).

For multilayer-network visualization, `pymnet` uses [matplotlib](https://matplotlib.org/) as its default backend, enabling users to exert low-level control over figure aesthetics to produce publication-quality plots. 
Support for interactive figures is provided via JavaScript and [D3.js](https://d3js.org/) as a backend.

To the best of our knowledge, the only other libraries offering tools to work with multilayer networks in Python are [multiNetX](https://github.com/nkoub/multinetx) and [py3plex](https://github.com/SkBlaz/py3plex), both of which appeared after `pymnet`. 
 Support for working with multilayer networks in Julia is offered by [MultilayerGraphs.jl](https://github.com/JuliaGraphs/MultilayerGraphs.jl) from @moroni2023, who also compile a list of R packages offering similar functionality. 

# Projects Using `pymnet`

`pymnet` has been used in numerous scientific publications across different disciplines, such as @kivela2014, @cozzo2015structure @kivela2017, @danchev2019centralized, @del2020multiplex, @zhou2020network, @baek2021social, @bergermann2021orientations, @sallmen2022, and @nurmi2023.

# Acknowledgments

This work was supported by the European Commission FET-Proactive project PLEXMATH (Grant No. 317614), the Academy of Finland (Grant No. 349366), and Digital Futures at KTH.

# References

