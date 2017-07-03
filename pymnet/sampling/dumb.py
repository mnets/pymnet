# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import itertools
from reqs import check_reqs, calculate_required_lengths

def dumbEnumeration(network,sizes,intersections,resultlist):
    req_nodelist_len,req_layerlist_len = calculate_required_lengths(sizes,intersections)
    for nodelist in list(itertools.combinations(list(network.iter_nodes()),req_nodelist_len)):
        for layerlist in list(itertools.combinations(list(network.iter_layers()),req_layerlist_len)):
                if check_reqs(network,nodelist,layerlist,sizes,intersections,(req_nodelist_len,req_layerlist_len)):
                    resultlist.append((list(nodelist),list(layerlist)))