"""Functions taking in networks and returning transformed versions of them.
"""
from net import *
import math
import itertools

def aggregate(net,aspects,newNet=None,selfEdges=False):
    """Reduces the number of aspects by aggregating them.

    This function aggregates edges from multilayer aspects together
    by summing their weights. Any number of aspects is allowed, and the
    network can have non-diagonal inter-layer links. The layers cannnot 
    be weighted such that they would have different coefficients when 
    the weights are summed together.

    Note that no self-links are created and all the inter-layer links
    are disregarded.

    Parameters
    ----------
    net : MultilayerNetwork
       The original network.
    aspects : int or tuple 
       The aspect which is aggregated over,or a tuple if many aspects
    newNet : MultilayerNetwork 
       Empty network to be filled and returned. If None, a new one is 
       created by this function.
    selfEdges : bool 
       If true aggregates self-edges too

    Returns
    -------
    net : MultiplexNetwork
       A new instance of multiplex network which is produced.

    Examples
    --------
    Aggregating the network with a singe aspect can be done as follows:

    >>> n=net.MultiplexNetwork([('categorical',1.0)])
    >>> an=transforms.aggregate(n,1)

    You need to choose which aspect(s) to aggregate over if the network 
    has multiple aspects:

    >>> n=MultiplexNetwork([2*('categorical',1.0)])
    >>> an1=transforms.aggregate(n,1)
    >>> an2=transforms.aggregate(n,2)
    >>> an12=transforms.aggregate(n,(1,2))
    """
    try:
        aspects=int(aspects)
        aspects=(aspects,)
    except TypeError:
        pass
    
    if newNet==None:
        newNet=MultilayerNetwork(aspects=net.aspects-len(aspects),
                                  noEdge=net.noEdge,
                                  directed=net.directed)
    assert newNet.aspects==net.aspects-len(aspects)
    for d in aspects:
        assert 0<d<=(net.aspects+1)


    for node in net:
        newNet.add_node(node,0)
    
    edgeIndices=filter(lambda x:math.floor(x/2) not in aspects,range(2*(net.aspects+1)))
    for edge in net.edges:
        newEdge=[]
        for index in edgeIndices:
            newEdge.append(edge[index])
        if selfEdges or not newEdge[0::2]==newEdge[1::2]:
            newNet[tuple(newEdge)]=newNet[tuple(newEdge)]+edge[-1]

    return newNet


def overlay_network(net):
    """Returns the overlay network of a multilayer network with 1 aspect.

    Returns
    -------
    net : MultiplexNetwork
       A new instance of multiplex network which is produced.
    """
    assert net.aspects==1
    newnet=MultilayerNetwork()
    for layer in net.slices[1]:
        for node1 in net.slices[0]:
            for node2 in net.slices[0]:
                if net.directed or node1>node2:
                    newnet[node1,node2]=newnet[node1,node2]+net[node1,node2,layer,layer]
    return newnet

def subnet(net,nodes,*layers):
    """Returns an induced subgraph with given set of nodes and layers.

    Parameters
    ----------
    net: The original network.
    nodes : sequence
        The nodes that span the induces subgraph.
    *layers : *sequence
        Layers included in the subgraph. One parameter for each aspect.

    Return
    ------
    subnet : type(net)
        The induced subgraph that contains only nodes given in
        `nodes` and the edges between those nodes that are
        present in `net`. Node properties etc are left untouched.
    """
    newNet=None
    if newNet==None:
        if type(net)==MultilayerNetwork:
            newNet=MultilayerNetwork(aspects=net.aspects,
                                     noEdge=net.noEdge,
                                     directed=net.directed)
            raise Exception("Not implemented yet.")
        elif type(net)==MultiplexNetwork:
            newNet=MultiplexNetwork(couplings=net.couplings,
                                           directed=net.directed,
                                           noEdge=net.noEdge,
                                           fullyInterconnected=net.fullyInterconnected)

            #Go through all the combinations of new layers
            for layer in itertools.product(*layers):
                degsum=0
                for node in nodes:        
                    degsum += net[(node,)+layer].deg()
                    newNet.add_node(node,0)

                if degsum >= len(nodes)*(len(nodes)-1)/2:
                    othernodes=set(nodes)
                    for node in nodes:
                        if not net.directed:
                            othernodes.remove(node)
                        for othernode in othernodes:
                            if net[(node,othernode)+layer]!=net.noEdge:
                                newNet[(node,othernode)+layer]=net[(node,othernode)+layer]
                else:
                    for node in nodes:
                        for neigh in itertools.imap(lambda x:x[0],net[(node,COLON)+layer]):
                            if neigh in nodes:
                                newNet[(node,neigh)+layer]=net[(node,neigh)+layer]

    return newNet
