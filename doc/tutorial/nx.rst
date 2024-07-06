Using NetworkX functions
========================

`NetworkX <https://networkx.github.io/>`_ is an excellent tool for network analysis, and there is no need to reinvent the wheel when working on monoplex networks with Pymnet. If you have NetworkX installed, you can use its functions directly with the multilayer-network objects produced by Pymnet.

Start by importing the library:

>>> from pymnet import nx, models

You can then run any NetworkX function from the pymnet.nx module. For example, you can produce the Karate Club network with the following command.

>>> net = nx.karate_club_graph()

This will produce a native Pymnet multilayer network object with 0 aspects (i.e., a monoplex network). To confirm this, try:

>>> net
<pymnet.net.MultilayerNetwork at 0x7f5b550eaa10>
>>> net.aspects
0

For the sake of reproducability in the next example, let's explicitly seed the ranom number generator here:

>>> import random
>>> random.seed(42)

You can also pass Pymnet objects as arguments to NetworkX functions in a similar way. This is handy, for example, when analyzing monoplex structures of intra-layer networks of multiplex networks. For example, producing a multiplex network with three Erdos-Renyi intra-layer networks using Pymnet and calculating the number of connected components in each layer can be done with the following command:

>>> {name: nx.number_connected_components(layer) for name, layer in models.er(1000, 3*[0.005]).A.items()}
{0: 10, 1: 9, 2: 5}
