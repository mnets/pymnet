Network types
=============

Monoplex networks
-----------------

Start by importing the library:

.. code-block:: python

    >>> from pymnet import *

:code:`MultilayerNetwork` is the basic network class in the library – all other types of networks are special cases of it. In order to get a monoplex network object, you can simply construct a :code:`MultilayerNetwork` with 0 aspects.

.. code-block:: python

    >>> net = MultilayerNetwork(aspects=0)

You can now start adding nodes to the network with the :code:`add_node` method:

.. code-block:: python

    >>> net.add_node(1)
    >>> net.add_node(2)

Iterating over the network object will yield all the nodes.

.. code-block:: python

    >>> list(net)
    [1, 2]

You can access the node objects of the network with the :code:`get` syntax. The node objects can be used, for example, to get the degree or strength of the node.

.. code-block:: python

    >>> net[1].deg()
    0

You can now start adding edges to your network. There are two basic ways of doing this. As the first option, you can use syntax which resembles setting elements in an adjacency matrix:

.. code-block:: python

    >>> net[1, 2] = 1

As a second option, you can first access a node object and then get the edge pointing to a neighbor of that node:

.. code-block:: python

    >>> net[1][2] = 1

These to ways are equivalent, but the difference will become important when we move on to networks that are not monoplex anymore. You can also add edges between nodes that you have not explicitly created, and in this case, the missing nodes are created automatically:

.. code-block:: python

    >>> net[1, 3] = 1
    >>> list(net)
    [1, 2, 3]

You can use similar syntax to check if the edges exist and to access their weights. The default weight value for non-existing edges is 0.

.. code-block:: python

    >>> net[1, 2]
    1
    >>> net[1][3]
    1
    >>> net[2,3]
    0

The network is undirected by default, which means that adding an edge in one direction automatically adds it in both directions.

.. code-block:: python

    >>> net[2, 1]
    1

The node objects can be iterated, which will yield the list of neighbors of the node:

.. code-block:: python

    >>> list(net[1])
    [2, 3]

The edges can be removed by simply setting their value to 0:

.. code-block:: python

    >>> net[1, 3] = 0
    >>> list(net[1])
    [2]

The edges of the networks can also be weighted with arbitrary numbers (except with the one corresponding to a missing edge). In weighted networks,
the degree and the weighted degree, i.e. strength, of a node are different:

.. code-block:: python

    >>> net[1,3] = 2
    >>> net[1].deg()
    2
    >>> net[1].strength()
    3

By default, all network objects are undirected. Directed network objects can be created by setting the keyword parameter :code:`directed` to :code:`True` in the constructor of the network object:

.. code-block:: python

    >>> dirnet = MultilayerNetwork(aspects=0, directed=True)
    >>> dirnet[1, 2] = 1
    >>> dirnet[1, 2]
    1
    >>> dirnet[2, 1]
    0
    >>> net[2, 1]
    1


Multilayer networks
-------------------

We are now ready to move to more general multilayer networks with an  arbitrary number of aspects. For simplicity, we will start with a network that has a single aspect.

.. code-block:: python

    >>> mnet = MultilayerNetwork(aspects=1)

Networks of this type are similar to the monoplex ones, but now you have layers in addition to nodes. You can add new layers with the :code:`add_layer` method:

.. code-block:: python

    >>> mnet.add_node(1)
    >>> mnet.add_layer("a")

Now, the node objects of the network need to be accessed by giving both the node and the layer:

.. code-block:: python

    >>> mnet[1, "a"].deg()
    0

Again, the edges can be accessed in two ways. The first one is similar to the tensor notation, where the indices of nodes and layers are grouped together. The following command will add an edge between node 1 in layer "a" and node 2 in layer "b" (again, the nodes and layers are implicitly created):

.. code-block:: python

    >>> mnet[1, 2, "a", "b"] = 1

In the syntax where you first access a node object and then its neighbor, the order of the indices is different. In this syntax, the following command is equivalent to the one shown above:

.. code-block:: python

    >>> mnet[1, "a"][2, "b"] = 1

You can again iterate over a node object, but this time, tuples with both node and layer are returned. Note that iterating over the network still returns only the nodes.

.. code-block:: python

    >>> list(mnet[1, "a"])
    [(2, 'b')]
    >>> list(mnet)
    [1, 2]

You can create networks with arbitrary number of aspects. The syntax for this type of networks is straight forward extension of the one described above.

.. code-block:: python

    >>> mnet2 = MultilayerNetwork(aspects=2)
    >>> mnet2[1, 2, "a" ,"b", "x" ,"y"] = 1
    >>> mnet2[1, "a", "x"][2, "b", "y"]
    1

Sometimes new syntax is needed. For example, the aspect must be specified when adding layers.

.. code-block:: python

    >>> mnet2.add_layer("c", 1)
    >>> mnet2.add_layer("z", 2)

.. more aspects
.. next: Slicing notation


Multiplex networks
------------------

The multilayer networks can in theory be used to represented multiplex networks, but in practice, it is often better to use a specialized class :code:`MultiplexNetwork` when dealing with multiplex networks.
There are several reasons for this. First, the :code:`MultiplexNetwork` class offers an additional convenient interface for handling intra-layer networks.
Second, the MultiplexNetwork class can take coupling rules as an input when it is constructed and use them to implicitly create the inter-layer edges when they are needed. This saves some memory and makes it easier to create networks with such coupling structures.
Third, using a :code:`MultiplexNetwork` will let the functions in the library know that your multilayer network is a multiplex network. Some of the functions only work for multiplex networks, but even the ones that work for general multilayer networks can use the information to speed up the processing.

The simplest multiplex network is the one with no coupling edges. You would create such an object with the following command:

:code:`MultiplexNetwork`

>>> mplex = MultiplexNetwork(couplings="none")

The nodes and edges can be accessed and added as usual:

.. code-block:: python

    >>> mplex[1, "a"][2, "a"] = 1

The difference to the :code:`MultilayerNetwork` object (in addition to not being able to add cross-layer links) is that you can now access the intra-layer networks as follows:

.. code-block:: python

    >>> mplex.A["a"][1, 2]
    1
    >>> mplex.A["a"][1, 3] = 1

You can construct :code:`MultiplexNetwork` objects with given coupling rules and have categorical or ordinal multiplex networks, where the inter-layer edges are filled in automatically.
In categorical networks, all the diagonal inter-layer edges are present.

.. code-block:: python

    >>> cnet = MultiplexNetwork(couplings="categorical")
    >>> cnet.add_node(1)
    >>> cnet.add_layer("a")
    >>> cnet.add_layer("b")
    >>> cnet[1, 1, "a", "b"]
    1

In ordinal networks, only adjacent layers are connected to each other. In a :code:`MultiplexNetwork` object, the layers of ordinal aspects must be integers.

.. code-block:: python

    >>> onet = MultiplexNetwork(couplings="ordinal")
    >>> onet.add_node("node")
    >>> onet.add_layer(1)
    >>> onet.add_layer(2)
    >>> onet.add_layer(3)
    >>> onet["node", "node", 1, 2]
    1
    >>> onet["node", "node", 1, 3]
    0

You can also give the coupling strength, i.e. the weight of the inter-layer edges, as a parameter

.. code-block:: python

    >>> cnet = MultiplexNetwork(couplings=("categorical", 10))
    >>> cnet.add_node(1)
    >>> cnet.add_layer("a")
    >>> cnet.add_layer("b")
    >>> cnet[1, 1, "a", "b"]
    10

Multiplex networks with multiple aspects can be constructed by passing a list of coupling rules as the coupling parameter in the constructor. For example,
the following code constructs a multiplex network where the first aspect is categorical and the second is ordinal.

.. code-block:: python

    >>> conet = MultiplexNetwork(couplings=["categorical", "ordinal"])
    >>> conet.add_node("node")
    >>> conet.add_layer("a", 1)
    >>> conet.add_layer("b", 1)
    >>> conet.add_layer(1, 2)
    >>> conet.add_layer(2, 2)
    >>> conet.add_layer(3, 2)
    >>> conet["node", "node", "a", "a", 1, 2]
    1.0

In this case, the intra-layer network must be accessed by giving a combination of layers.

.. code-block:: python

    >>> conet.A[("a", 1)]["node", "node2"] = 1

