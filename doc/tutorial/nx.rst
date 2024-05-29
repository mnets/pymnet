Using NetworkX functions
========================

`NetworkX <https://networkx.github.io/>`_ is an excellent tool for network analysis, and there is no need to reinvent the wheel when working on monoplex networks with Pymnet. If you have NetworkX installed, you can use its functions directly with the multilayer-network objects produced by Pymnet.

Start by importing the library:

>>> from pymnet import nx

You can then run any NetworkX function from the pymnet.nx module. For example, you can produce the Karate Club network with the following command.

>>> net = nx.karate_club_graph()

This will produce a native Pymnet multilayer network object with 0 aspects (i.e., a monoplex network). To confirm this, try:

>>> print(net)
<pymnet.net.MultilayerNetwork at 0x7f5b550eaa10>

You can also pass Pymnet objects as arguments to NetworkX functions in a similar way. This is handy, for example, when analyzing monoplex structures of intra-layer networks of multiplex networks. For example, producing a multiplex network with three Erdos-Renyi intra-layer networks using Pymnet and calculating the number of connected components in each layer can be done with the following command:

>>> print(map(nx.number_connected_components,models.er(1000,3*[0.005]).A.values()))
[10, 9, 5]

This result was generated with :code:`random.seed(42))` (after runnign :code:`import random`).
Your output may differ depending on the seed of the random-number generator used by the :code:`random` module.
