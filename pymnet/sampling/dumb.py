# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import itertools
from reqs import default_check_reqs, default_calculate_required_lengths

def dumbEnumeration(network,sizes,intersections,resultlist):
    u"""Enumerates all induced subgraphs of the form [nodelist][layerlist] by
    going through all possible [nodelist][layerlist] combinations and checking
    whether they fulfill the requirements. This is a dumb algorithm and is not
    intended for use in large networks.
    
    Parameters
    ----------
    network : MultilayerNetwork
        The multilayer network to be analyzed.
    sizes : list of ints > 0
        How many nodes are on each layer of the induced subgraphs that we want
        to discover.
    intersections : list of ints >= 0
        How large are the intersections between groups of layers. The layer roles
        are in the same order as in sizes. For a more detailed description
        of how to construct the intersections list, see :func:'reqs.check_reqs'.
    resultlist : list
        Where found induced subgraphs are appended as tuples (nodelist, layerlist).
    """
    req_nodelist_len,req_layerlist_len = default_calculate_required_lengths(sizes,intersections)
    for nodelist in list(itertools.combinations(list(network.iter_nodes()),req_nodelist_len)):
        for layerlist in list(itertools.combinations(list(network.iter_layers()),req_layerlist_len)):
                if default_check_reqs(network,nodelist,layerlist,sizes,intersections,req_nodelist_len,req_layerlist_len):
                    resultlist.append((list(nodelist),list(layerlist)))