Tutorial
========


Downloading and installing
--------------------------

You can download the latest source files directly from the repository http://bitbucket.org/bolozna/multilayer-networks-library/ as a zip file. Alternatively,
you can use Mercurial to clone the repository:

.. code-block:: none

   $ hg clone https://bitbucket.org/bolozna/multilayer-networks-library

The current version of the library is written purely in Python, and simply adding the library directory to your Python path is enough to start using it.


Monoplex networks
-----------------

Start by importing the library:

>>> from pymnet import *

MultilayerNetwork is the basic network class in the library -- all other types of networks are special case of it. In order to get a monoplex network object
you can simply construct a MultilayerNetwork with 0 aspects.

>>> net = MultilayerNetwork(aspects=0)

You can now start adding nodes to the network with the 'add_node' method:

>>> net.add_node(1)
>>> net.add_node(2)

Iterating the network object will yield all the nodes.

>>> list(net)
[1, 2]

You can access node objects of the network with the get syntax. The node objects can be used for example to get the degree or strength of the node.

>>> net[1].deg()
0

You can now start adding edges to your network. There are two basic ways of doing this. First is the syntax which resembles setting elements in an adjacency matrix:

>>> net[1,2] = 1

In the second way, you first access a node object and then get the edge pointing to a neighbor of that node:

>>> net[1][2] = 1

These to ways are equivalent, but the difference will become important when we move on to networks which are not monoplex ones. You can also add edges between nodes that you have not explicitly created, and in this case the missing nodes are created automatically:

>>> net[1,3] = 1
>>> list(net)
[1, 2, 3]

You can use similar syntax to check if the edges exist and access their weights. The default weight value for non-existing edge is 0.

>>> net[1,2]
1
>>> net[1][3]
1
>>> net[2,3]
0

The node objects can be iterated, which will yield the list of neighbors of the node:

>>> list(net[1])
[2, 3]

The edges can be removed by simply setting their value to 0:

>>> net[1,3] = 0
>>> list(net[1])
[2]

The edges of the networks can also be weighted with arbitrary numbers (except with the one corresponding to a missing edge). In the weighted networks
the degree and the weighted degree, i.e. strength, of a node are different:

>>> net[1,3] = 2
>>> net[1].deg()
2
>>> net[1].str()
3

By default, all the network objects are undirected. The directed network objects can be accessed by giving a keyword parameter 'directed' to True in the constructor
of the network object:

>>> dirnet = MultilayerNetwork(aspects=0,directed=True)
>>> dirnet[1,2]=1
>>> dirnet[1,2]
1
>>> dirnet[2,1]
0
>>> net[2,1]
1


Multilayer networks
-------------------

We are now ready to move to more general multilayer networks with arbitrary number of aspects. For simplicity, we will start with a network with a single aspect.

>>> mnet = MultilayerNetwork(aspects=1)

In these type of networks are similar to the monoplex ones, but now you have layers in addition of nodes. You can add new layers with the 'add_layer' method:

>>> mnet.add_node(1)
>>> mnet.add_layer('a')

Now, the node objects of the network need to be accessed by giving both the node and the layer:

>>> mnet[1,'a'].deg()
0

Again, the edges can be accessed in two ways. First one is similar to the tensor notation where the indices of nodes and layers are grouped together. The following command
will add an edge between node 1 in layer 'a' to node 2 in layer 'b' (again, the nodes and layers are implicitely created):

>>> mnet[1,2,'a','b'] = 1

In the syntax where you first access a node object and then it's neighbor the order of the indices is different. In this syntax the following command is equivalent to the one shown above:

>>> mnet[1,'a'][2,'b'] = 1

You can again iterate over a node object, but this time tuples with both node and layer are returned. Note that iterating over the network still returns only the nodes.

>>> list(mnet[1,'a'])
[(2, 'b')]
>>> list(mnet)
[1, 2]

.. next: Slicing notation


Multiplex networks
------------------

