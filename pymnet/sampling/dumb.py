# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import itertools
from reqs import default_check_reqs,default_calculate_required_lengths,relaxed_check_reqs

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
    if custom_check_function != None:
        assert nnodes != None and nlayers != None, "Please provide nnodes and nlayers when using a custom check function"
        req_nodelist_len = nnodes
        req_layerlist_len = nlayers
        check_function = custom_check_function
    if sizes != None and intersections != None and check_function == None:
        if isinstance(intersections,list):
            if None in intersections:
                assert nnodes != None, "Please provide nnodes if including Nones in intersections"
                req_nodelist_len = nnodes
                req_layerlist_len = len(sizes)
            else:
                if intersection_type == "strict":
                    assert nnodes == None and nlayers == None, "You cannot provide both sizes and intersections and nnodes and nlayers, if intersections is a list"
                    req_nodelist_len, req_layerlist_len = default_calculate_required_lengths(sizes,intersections)
                elif intersection_type == "less_or_equal":
                    assert nnodes != None and nlayers == None, "please provide nnodes (and not nlayers) if using less_or_equal intersection type"
                    req_nodelist_len = nnodes
                    req_layerlist_len = len(sizes)
            check_function = lambda x,y,z: default_check_reqs(x,y,z,sizes,intersections,req_nodelist_len,req_layerlist_len,intersection_type)
        elif isinstance(intersections,int):
            assert intersections >= 0, "Please provide nonnegative common intersection size"
            assert nnodes != None and nlayers == None, "When requiring only common intersection size, please provide nnodes (and not nlayers)"
            req_nodelist_len = nnodes
            req_layerlist_len = len(sizes)
            intersections_as_list = [None]*(2**len(sizes)-len(sizes)-1)
            intersections_as_list[-1] = intersections
            check_function = lambda x,y,z: default_check_reqs(x,y,z,sizes,intersections_as_list,req_nodelist_len,req_layerlist_len,intersection_type)
            #check_function = lambda x,y,z: check_only_common_intersection(x,y,z,intersections,intersection_type)
    if nnodes != None and nlayers != None and check_function == None:
        assert sizes == None and intersections == None, "You cannot provide both sizes and intersections and nnodes and nlayers, if intersections is a list"
        req_nodelist_len = nnodes
        req_layerlist_len = nlayers
        assert isinstance(req_nodelist_len,int) and isinstance(req_layerlist_len,int), "Non-integer nnodes or nlayers"
        assert req_nodelist_len > 0 and req_layerlist_len > 0, "Nonpositive nnodes or nlayers"
        check_function = relaxed_check_reqs
    assert check_function != None, "Please specify a valid combination of parameters to determine method of subgraph validity checking"
    
    for nodelist in list(itertools.combinations(list(network.iter_nodes()),req_nodelist_len)):
        for layerlist in list(itertools.combinations(list(network.iter_layers()),req_layerlist_len)):
                if check_function(network,nodelist,layerlist):
                    resultlist.append((list(nodelist),list(layerlist)))