# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""
import pymnet
from pymnet import nx
import itertools

def default_check_reqs(network,nodelist,layerlist,**kwargs):
#def default_check_reqs(network,nodelist,layerlist,sizes,intersections,(req_nodelist_len,req_layerlist_len)=(None,None)):
    u"""Checks whether an induced subgraph of the form [nodelist][layerlist] fulfills
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
        of these numbers, do not use this parameter. Mainly intended for use inside
        scripts.
        
    Returns
    -------
    True if the requirements are fulfilled, False otherwise.
    
    Constructing the requirements
    -----------------------------
    The sizes list contains the desired number of nodes on each layer in any order.
    This means that the layers in the actual found sub-network can be in any order.
    However, the order of sizes determines the order of entries in intersections.
    The intersections list is constructed as follows:
        First, think of each size in the size list as having a specific role:
        the first entry in sizes corresponds to layer role A, the second to role
        B, the third to role C, and so on. This order determines how intersections
        in the intersections list are interpreted when checking if the requirements
        are fulfilled.
        
        Then, construct the intersections list so that first all size-two intersections
        are listed, then size-three intersections, and so on, until the intersection
        between all layers is reached. The order of listing size n-intersections is
        such that the closer the role is to the beginning of the size list, the later
        it is iterated over. More specifically, this is the order that itertools.combinations()
        uses to iterate. Since we signify the roles by letters A, B, C and so
        on, this means that the intersections are listed in "alphabetical order"
        within each size category.
    
    For example, suppose we have a length-four sizes list. Now, we think of the first
    size entry as layer (role) A, the second as layer B, the third as layer C, and the fourth
    as layer D. The intersections list is then assumed to contain the intersections
    in the following order:
    
    intersections = [A∩B, A∩C, A∩D, B∩C, B∩D, C∩D, A∩B∩C, A∩B∩D, A∩C∩D, B∩C∩D, A∩B∩C∩D]
    
    When checking whether the size and intersection requirements are fulfilled,
    each possible set of role assginments to the actual layers is checked. If even
    one is suitable, the function returns True.
    Continuing from the example above, if the actual induced subgraph has layers [X,Y,Z,W],
    all possible role assignment combinations are checked (X takes role from {A,B,C,D}, Y 
    takes role from {A,B,C,D} minus {role(X)}, Z takes role from {A,B,C,D} minus {role(X),role(Y)}, W
    takes role from {A,B,C,D} minus {role(X),role(Y),role(Z)}). This also means that
    the orderings of the [nodelist] and [layerlist] of the induced subgraph to be
    tested do not matter.
    """
    #if (req_nodelist_len,req_layerlist_len) == (None,None):
    #    try:
    #        req_nodelist_len,req_layerlist_len = default_calculate_required_lengths(sizes,intersections)
    #    except AssertionError:
    #        raise
    try:
        sizes = kwargs['sizes']
        intersections = kwargs['intersections']
    except KeyError:
        raise TypeError, "Please specify sizes and intersections"
    if 'req_nodelist_len' not in kwargs or 'req_layerlist_len' not in kwargs:
        try:
            req_nodelist_len,req_layerlist_len = default_calculate_required_lengths(**kwargs)
        except AssertionError:
            raise
    else:
        req_nodelist_len = kwargs['req_nodelist_len']
        req_layerlist_len = kwargs['req_layerlist_len']
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
            for ii in range(1,len(layerlist)+1): # A, B etc. AB, AC etc.
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
    
    
    
def default_calculate_required_lengths(**kwargs):
    """Returns the required nodelist length and required layerlist length of
    and induced subgraph of the form [nodelist][layerlist] determined by the
    given requirements.
    """
    try:
        sizes = kwargs['sizes']
        intersections = kwargs['intersections']
    except KeyError:
        raise TypeError, "Please specify sizes and intersections"
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