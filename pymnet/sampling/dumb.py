# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import itertools
from reqs import default_check_reqs, default_calculate_required_lengths
import pymnet
from pymnet import nx

def dumbEnumeration(network,resultlist,sizes=None,intersections=None,nnodes=None,nlayers=None,intersection_type="strict",custom_check_function=None):
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
    check_function = None
    assert (sizes != None and intersections != None) or (nnodes != None and nlayers != None), "Please provide either sizes and intersections or nnodes and nlayers"
    if sizes != None: # Work in progress
        assert intersections != None and nnodes == None and nlayers == None, "Please provide intersections when providing sizes, and not nnodes or nlayers"
        req_nodelist_len, req_layerlist_len = default_calculate_required_lengths(sizes,intersections)
        check_function = lambda x,y,z: default_check_reqs(x,y,z,sizes,intersections,req_nodelist_len,req_layerlist_len)
    if nnodes != None:
        assert nlayers != None and sizes == None and intersections == None, "Please provide nlayers when providing nnodes, and not sizes or intersections"
        req_nodelist_len = nnodes
        req_layerlist_len = nlayers
        assert isinstance(req_nodelist_len,int) and isinstance(req_layerlist_len,int), "Non-integer nnodes or nlayers"
        assert req_nodelist_len > 0 and req_layerlist_len > 0, "Nonpositive nnodes or nlayers"
        check_function = dumb_enumeration_relaxed_check_function
    if custom_check_function != None:
        assert nnodes != None and nlayers != None, "Please provide nnodes and nlayers when using a custom check function"
        check_function = custom_check_function
    assert check_function != None, "Please specify a method of subgraph validity checking"
    
    for nodelist in list(itertools.combinations(list(network.iter_nodes()),req_nodelist_len)):
        for layerlist in list(itertools.combinations(list(network.iter_layers()),req_layerlist_len)):
                if check_function(network,nodelist,layerlist):
                    resultlist.append((list(nodelist),list(layerlist)))
                    
def dumb_enumeration_relaxed_check_function(network,nodelist,layerlist):
    induced_graph = pymnet.subnet(network,nodelist,layerlist)
    try:
        graph_is_connected = nx.is_connected(pymnet.transforms.get_underlying_graph(induced_graph))
    except nx.networkx.NetworkXPointlessConcept:
        return False
    if graph_is_connected:
        return True
    else:
        return False