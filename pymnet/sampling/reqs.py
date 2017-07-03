# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""
import pymnet
from pymnet import nx
import PyBliss
#import matplotlib.pyplot as plt
import itertools
#from operator import itemgetter
#import numpy as np

def check_reqs(network,nodelist,layerlist,sizes,intersections,(req_nodelist_len,req_layerlist_len)=(None,None)):
    '''
    One aspect.
    Inappropriate required lengths are intentionally not checked for, if you
    aren't sure you can provide correct lengths leave them out of the parameters.
    '''
    if (req_nodelist_len,req_layerlist_len) == (None,None):
        try:
            req_nodelist_len,req_layerlist_len = calculate_required_lengths(sizes,intersections)
        except AssertionError:
            raise
    assert len(nodelist) == req_nodelist_len, "Wrong number of nodes"
    assert len(layerlist) == req_layerlist_len, "Wrong number of layers"
    induced_graph = pymnet.subnet(network,nodelist,layerlist)
    try:
        graph_is_connected = nx.is_connected(pymnet.transforms.get_underlying_graph(induced_graph))
    except nx.networkx.NetworkXPointlessConcept:
        return False
    if graph_is_connected:   
        d = dict() # keys: layers, values: nodes
        for nodelayer in list(induced_graph.iter_node_layers()):
            d.setdefault(nodelayer[1],[])
            d[nodelayer[1]].append(nodelayer[0])
        if len(d) != len(layerlist):
            return False   
        d_isect = dict() # layer intersections, roles 0,1,2,...
        indexer = 0
        for jj in range(2,len(layerlist)+1):
            for combination in list(itertools.combinations(list(range(0,len(layerlist))),jj)):
                d_isect[combination] = intersections[indexer]
                indexer = indexer + 1
        for permutation in list(itertools.permutations(layerlist)):
            goto_next_perm = False
            # check all intersections and sizes
            for ii in range(1,len(layerlist)+1): # A, B ect. AB, AC etc.
                for combination in list(itertools.combinations(permutation,ii)): # try all role combinations
                    assert len(combination) >= 1, "Empty combination list, this shouldn't happen"
                    if len(combination) == 1:
                        if len(d[combination[0]]) != sizes[permutation.index(combination[0])]:
                            goto_next_perm = True
                            break
                    elif len(combination) > 1:
                        rolelist = []
                        nodeset = set(d[combination[0]])
                        for layer in combination:
                            rolelist.append(permutation.index(layer))
                            nodeset = nodeset & set(d[layer])
                        rolelist.sort()
                        if len(nodeset) != d_isect[tuple(rolelist)]:
                            goto_next_perm = True
                            break
                if goto_next_perm:
                    break
            if not goto_next_perm:
                return True    # tarkista logiikka
    return False
    
    
    
def calculate_required_lengths(sizes,intersections):
    assert sizes != [], "Empty layer size list"
    assert len(intersections) == 2**len(sizes)-len(sizes)-1, "Wrong number of intersections"
    assert all(i>=1 and isinstance(i,int) for i in sizes) and all(j>=0 and isinstance(j,int) for j in intersections), "Inappropriate intersections or sizes"
    if not intersections:
        return sizes[0],1
    layerlist_length = len(sizes)
    nodelist_length = sum(sizes)
    index = 0
    for ii in range(2,len(sizes)+1):
        for _ in list(itertools.combinations(sizes,ii)):
            if ii % 2 == 0:
                nodelist_length = nodelist_length - intersections[index]
                index = index + 1
            else:
                nodelist_length = nodelist_length + intersections[index]
                index = index + 1
    return nodelist_length,layerlist_length