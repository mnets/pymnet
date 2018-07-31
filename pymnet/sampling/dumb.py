# -*- coding: utf-8 -*-

import itertools
from .reqs import default_check_reqs,default_calculate_required_lengths,relaxed_check_reqs

def dumb_enumeration(network,results,sizes=None,intersections=None,nnodes=None,nlayers=None,intersection_type="strict",custom_check_function=None):
    """Enumerates all induced subgraphs of the form [nodelist][layerlist] by
    going through all possible [nodelist][layerlist] combinations and checking
    whether they fulfill the requirements. This is a naive algorithm and is not
    intended for use in large networks.
    
    Accepts the same parameters as sample_multilayer_subgraphs_esu, and has the same functionalities
    (except when using a custom_check_function, where induced subgraphs passed to
    the check function are different between this and sample_multilayer_subgraphs_esu, which needs to
    be handled by the user - see below).
    
    A difference between this and sample_multilayer_subgraphs_esu is that in this function, no
    guarantees other than nnodes and nlayers being correct are made about the
    induced subgraphs passed to the validity checking function (unlike in sample_multilayer_subgraphs_esu,
    where they are guaranteed to have at least some path in them and have no empty nodes or
    layers.) That is, the induced subgraphs are probably not connected, they might contain
    empty layers or nodes, etc. If you use a custom_check_function, take this into account.
    If using one of the built-in functionalities which use default_check_reqs or
    relaxed_check_reqs, this has been taken into account and you don't have to worry about it.
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
                    if isinstance(results,list):
                        results.append((list(nodelist),list(layerlist)))
                    elif callable(results):
                        results((list(nodelist),list(layerlist)))
                    else:
                        raise TypeError("Please provide results container as list or callable")