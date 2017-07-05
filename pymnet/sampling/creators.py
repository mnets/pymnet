# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""
import pymnet
import random
import numpy as np

def multilayer_partially_interconnected(nodes_by_layer,p):
    """Create a one-aspect E-R multilayer network with given nodesets for each
    layer and edge probability p.
    
    Parameters
    ----------
    nodes_by_layer : list of lists
        A list where each element is a list of nodes on a layer.
    p : float 0 <= p <= 1
        The probability that an edge exists between a node-layer pair.
    """
    network = pymnet.MultilayerNetwork(aspects=1,fullyInterconnected=False)
    for layer,nodelist in enumerate(nodes_by_layer):
        network.add_layer(layer)
        for node in nodelist:
            network.add_node(node=node,layer=layer)
    numberings = dict()
    for index,nodelayer in enumerate(list(network.iter_node_layers())):
        numberings[nodelayer] = index
    for nodelayer1 in numberings:
        for nodelayer2 in numberings:
            if numberings[nodelayer1] > numberings[nodelayer2] and random.random() < p:
                network[nodelayer1][nodelayer2] = 1
    return network
    
def random_nodelists(poolsize,nodes_per_layer,layers,replace=True):
    # nodes_per_layer is the maximum, overlaps may occur
    arr = np.random.choice(poolsize,size=(layers,nodes_per_layer),replace=replace)
    return [list(nodelist) for nodelist in arr]