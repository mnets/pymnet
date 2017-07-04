# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""
import pymnet
from pymnet import nx
import itertools

def check_reqs(network,nodelist,layerlist,sizes,intersections,(req_nodelist_len,req_layerlist_len)=(None,None)):
    """Checks whether an induced subgraph of the form [nodelist][layerlist] fulfills
    the given requirements.
    
    Parameters
    ----------
    network : MultilayerNetwork
        The network containing the induced subgraph.
    nodelist : list of node names
        The nodes in the induced subgraph.
    layerlist : list of layer names
        The layers in the induced subgraph.
    sizes : list of ints > 0
        How many nodes should be on each layer of an acceptable induced subgraph.
    intersections : list of ints >= 0
        How many nodes should be shared between sets of layers in an acceptable
        induced subgraph.
    (req_nodelist_len, req_layerlist_len) : tuple of ints
        How long an acceptable nodelist (union of all nodes in the induced subgraph)
        and an acceptable layerlist should be. If you cannot guarantee the correctness
        of these numbers, leave this parameter empty. Mainly intended for use inside
        scripts.
        
    Returns
    -------
    True if requirements are fulfilled, False otherwise.
    """
    if (req_nodelist_len,req_layerlist_len) == (None,None):
        try:
            req_nodelist_len,req_layerlist_len = calculate_required_lengths(sizes,intersections)
        except AssertionError:
            raise
    assert len(nodelist) == req_nodelist_len, "Wrong number of nodes"
    assert len(layerlist) == req_layerlist_len, "Wrong number of layers"
    assert all(i>=1 for i in sizes), "Inappropriate sizes"
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
        if len(d) != req_layerlist_len:
            return False   
        d_isect = dict() # layer intersections, roles 0,1,2,...
        indexer = 0
        for jj in range(2,len(layerlist)+1):
            for combination in list(itertools.combinations(list(range(0,len(layerlist))),jj)):
                d_isect[combination] = intersections[indexer]
                indexer = indexer + 1
        for permutation in list(itertools.permutations(layerlist)):
            # index in permutation determines role of layer
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
                return True
    return False
    
    
    
def calculate_required_lengths(sizes,intersections):
    """Returns the required nodelist length and required layerlist length of
    and induced subgraph of the form [nodelist][layerlist] determined by the
    given requirements.
    """
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