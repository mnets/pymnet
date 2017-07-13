# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""
import pymnet
import random

def multilayer_partially_interconnected(nodes_by_layer,p,seed=None):
    """Create a one-aspect E-R multilayer network with given nodesets for each
    layer and edge probability p.
    
    Parameters
    ----------
    nodes_by_layer : sequence/iterator of sequences/iterators
        A sequence where each element is a sequence of nodes on a layer.
    p : float 0 <= p <= 1
        The probability that an edge exists between a node-layer pair.
    seed : int, str, bytes or bytearray
        Seed for network generation.
        
    Returns
    -------
    The generated network.
    """
    if seed == None:
        random.seed()
    else:
        random.seed(seed)
    network = pymnet.MultilayerNetwork(aspects=1,fullyInterconnected=False)
    for layer,nodelist in enumerate(nodes_by_layer):
        network.add_layer(layer)
        for node in nodelist:
            network.add_node(node=node,layer=layer)
    numberings = dict()
    for index,nodelayer in enumerate(network.iter_node_layers()):
        numberings[nodelayer] = index
    for nodelayer1 in numberings:
        for nodelayer2 in numberings:
            if numberings[nodelayer1] > numberings[nodelayer2] and random.random() < p:
                network[nodelayer1][nodelayer2] = 1
    return network
    
def random_nodelists(poolsize,nodes_per_layer,layers,seed=None):
    # nodes_per_layer is exact, no overlaps
    if seed == None:
        random.seed()
    else:
        random.seed(seed)
    for _ in range(layers):
        yield random.sample(xrange(poolsize),nodes_per_layer)