# -*- coding: utf-8 -*-

import pymnet
#from pymnet import nx
import itertools

def default_check_reqs(network,nodelist,layerlist,sizes,intersections,nnodes=None,nlayers=None,intersection_type="strict"):
    u"""Checks whether a multilayer induced subgraph of the form [nodelist][layerlist] is connected,
    whether it has no empty layers or nodes, and whether it fulfills the given sizes and intersections
    requirements. Works on one-aspect multilayer networks.
    
    Parameters
    ----------
    network : MultilayerNetwork
        A one-aspect multilayer network containing the induced subgraph.
    nodelist : list of node names
        The nodes in the induced subgraph.
    layerlist : list of layer names
        The layers in the induced subgraph.
    sizes : list of ints > 0
        How many nodes should be on each layer of an acceptable induced subgraph.
        One integer for each layer of an acceptable subgraph.
    intersections : list of ints >= 0 or Nones
        How many nodes should be shared between sets of layers in an acceptable
        induced subgraph. If an entry in the list is None, any number of shared
        nodes is accepted. The order of the intersections is taken to follow the
        order of layers in sizes, with two-layer intersections being listed first,
        then three-layer intersections, etc. For more details, see section
        "Constructing the requirements".
    nnodes : int
        How many nodes an acceptable subgraph should have. If not provided, it
        will be calculated based on the sizes and intersections parameters.
        Required if there are Nones in intersections or if intersection_type
        is not "strict". If you cannot guarantee the correctness of this
        number, do not use this parameter. Can be used in scripts to bypass
        calculating the correct number of nodes based on the sizes and intersections
        parameters.
    nlayers : int
        How many layers an acceptable subgraph should have. If not provided, it
        will be calculated based on the sizes and intersections parameters.
        Required if there are Nones in intersections.
        If you cannot guarantee the correctness of this number, do not use this
        parameter. Can be used in scripts to bypass calculating the correct number
        of layers based on the sizes and intersections parameters.
    intersection_type : string, "strict" or "less_or_equal"
        If intersection_type is "strict", all intersections must be exactly equal
        to entries in the intersections parameter. If intersection_type is
        "less_or_equal", an intersection is allowed to be less than or equal to the corresponding
        entry in the intersections parameter. Usage is case-sensitive.
        
    Returns
    -------
    True if the requirements are fulfilled, the induced subgraph has no empty nodes
    or layers, and the induced subgraph is connected. False otherwise.
    
    Empty nodes or layers
    ---------------------
    The phrase 'does not contain any empty layers or nodes' means that for each
    layer, there is at least one nodelayer in the induced subgraph, and that for
    each node, there is at least one nodelayer in the induced subgraph.
    In other words, each node in the nodelist and each layer in the layerlist
    appears at least once as the node identity or the layer identity, respectively,
    among the nodelayers present in the induced subgraph.
    
    Constructing the requirements
    -----------------------------
    The sizes list contains the desired number of nodes on each layer in any order.
    This means that the layers in the actual found sub-network can be in any order.
    However, the order of entries in sizes determines the order of entries in intersections.
    The intersections list is constructed as follows:
        First, think of each size in the size list as having a specific role:
        the first entry in sizes corresponds to layer role A, the second to role
        B, the third to role C, and so on. This order determines how intersections
        in the intersections list are interpreted when checking if the requirements
        are fulfilled.
        
        Then, construct the intersections list so that first all size-two intersections
        are listed, then size-three intersections, and so on, until the intersection
        between all layers is reached. The entry for each intersection can be an integer
        or None. An integer signifies the number of nodes in the intersection (the cardinality
        of the intersection set), and it can be followed strictly or less strictly, depending
        on the intersection_type parameter. The value None signifies that the intersection in
        question can have any size in an acceptable induced subgraph. If intersections
        contains Nones, the nnodes and nlayers parameters must also be specified.
        
        The order of listing size-n intersections is such that the closer the role is
        to the beginning of the size list, the later it is iterated over. More specifically,
        this is the order that itertools.combinations() uses to iterate. Since we signify
        the roles by letters A, B, C and so on, this means that the intersections are
        listed in "alphabetical order" within each size category.
    
    For example, suppose we have a length-four sizes list. Now, we think of the first
    size entry as layer (role) A, the second as layer B, the third as layer C, and the fourth
    as layer D. The intersections list is then assumed to contain the intersections
    in the following order:
    
    intersections = [A∩B, A∩C, A∩D, B∩C, B∩D, C∩D, A∩B∩C, A∩B∩D, A∩C∩D, B∩C∩D, A∩B∩C∩D]
    
    When checking whether the size and intersection requirements are fulfilled,
    each possible set of role assignments to the actual layers is checked. If even
    one is suitable, the function returns True.
    
    Continuing from the example above, if the actual induced subgraph has layers [X,Y,Z,W],
    all possible role assignment combinations are checked (X takes role from the set {A,B,C,D}, Y 
    takes role from {A,B,C,D} minus {role(X)}, Z takes role from {A,B,C,D} minus {role(X),role(Y)}, W
    takes role from {A,B,C,D} minus {role(X),role(Y),role(Z)}). The role assignment is iterated
    until an acceptable role assignment is found -- at which point the function returns True --
    or until all possible role assignments have been considered without success -- at which
    point the function returns False.
    
    This also means that the orderings of the [nodelist] and [layerlist] of the induced subgraph
    to be tested do not matter (i.e calling this function with nodelist = [1,2] and layerlist = ['X','Y']
    gives the exact same return value as nodelist = [2,1] and layerlist = ['Y','X'], etc.).
    
    Using Nones
    -----------
    If we only care about the cardinalities of some specific intersections, we can set
    the rest to None. For example, calling
    
    >>> default_check_reqs(some_network,some_nodelist,some_layerlist,[1,2,3],[None,None,2,None],nnodes=4,nlayers=3)
    
    means that the algorithm will find the induced subgraphs which are connected, have 4 nodes and
    3 layers, have no empty layers or nodes, have one node on one layer, two nodes on another layer,
    three nodes on the third layer, and have a cardinality-2 (size-2) intersection between the layer
    that has two nodes and the layer that has three nodes (with no constraints on the cardinalities
    of the other intersections).
    
    When using Nones, nnodes and nlayers have to be specified, since if all intersection
    cardinalities are not unambiguous, the nnodes and nlayers cannot be calculated based
    on the sizes and intersections alone. It is up to the user to provide nnodes and nlayers
    that are sensible (for example, nnodes cannot sensibly be more than the sum of all sizes).
    It is also up to the user to not give contradictory requirements.
    Technically, only nnodes would be required, but both have to be given to make the function
    call more explicit and more intuitive to read.
    
    Example
    -------
    Suppose we have the multilayer network N:
    
    (1,'X')----(2,'X')    (3,'X')
                  |
                  |
               (2,'Y')
             
    where (a,b) are nodelayer tuples with a = node identity and b = layer identity.
    Now,
    
    >>> default_check_reqs(N,[1,2],['X','Y'],[1,2],[1])
    
    returns True, as do
    
    >>> default_check_reqs(N,[2,1],['Y','X'],[1,2],[1])
    
    and
    
    >>> default_check_reqs(N,[1,2],['Y','X'],[2,1],[1])
    
    (and naturally so do also all the other ways of defining the same induced subgraph
    and the same requirements).
    
    On the other hand,
    
    >>> default_check_reqs(N,[2,3],['X','Y'],[1,2],[1])
    
    returns False, since the induced subgraph is not connected.
    """
    if intersection_type == "strict":
        if nnodes != None and nlayers != None:
            req_nodelist_len = nnodes
            req_layerlist_len = nlayers
        else:
            if None in intersections:
                raise TypeError("Please provide nnodes and nlayers when including Nones in intersections")
            try:
                req_nodelist_len,req_layerlist_len = default_calculate_required_lengths(sizes,intersections)
            except AssertionError:
                raise
            
    elif intersection_type == "less_or_equal":
        assert nnodes != None, "Please provide nnodes when using less_or_equal intersection type"
        if nlayers != None:
            req_nodelist_len = nnodes
            req_layerlist_len = nlayers
        else:
            if None in intersections:
                raise TypeError("Please provide nnodes and nlayers when including Nones in intersections")
            req_nodelist_len = nnodes
            try:
                _,req_layerlist_len = default_calculate_required_lengths(sizes,intersections)
            except AssertionError:
                raise
        
    else:
        raise TypeError("Please specify either strict or less_or_equal as intersection type")

    assert len(nodelist) == req_nodelist_len, "Wrong number of nodes"
    assert len(layerlist) == req_layerlist_len, "Wrong number of layers"
    assert all(i>=1 for i in sizes), "Inappropriate sizes"
    induced_graph = pymnet.subnet(network,nodelist,layerlist)
    try:
        graph_is_connected = pymnet.nx.is_connected(pymnet.transforms.get_underlying_graph(induced_graph))
    except pymnet.nx.networkx.NetworkXPointlessConcept:
        return False
    if graph_is_connected:
        
        # check for empty nodes or layers
        nls = set(induced_graph.iter_node_layers())
        for layer in layerlist:
            no_nodelayers = True
            for node in nodelist:
                if (node,layer) in nls:
                    no_nodelayers = False
                    break
            if no_nodelayers:
                return False
        for node in nodelist:
            no_nodelayers = True
            for layer in layerlist:
                if (node,layer) in nls:
                    no_nodelayers = False
                    break
            if no_nodelayers:
                return False        
        
        d = dict() # keys: layers, values: nodes
        for nodelayer in nls:
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
                    if len(combination) == 1: # check sizes
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
                        if intersection_type == "strict":
                            if d_isect[tuple(rolelist)] != None and len(nodeset) != d_isect[tuple(rolelist)]:
                                goto_next_perm = True
                                break
                        elif intersection_type == "less_or_equal":
                            if d_isect[tuple(rolelist)] != None and len(nodeset) > d_isect[tuple(rolelist)]:
                                goto_next_perm = True
                                break
                if goto_next_perm:
                    break
            if not goto_next_perm:
                return True
    return False
    
    
    
def default_calculate_required_lengths(sizes,intersections):
    """Returns the required number of nodes and the required number of layers of
    a one-aspect induced subgraph of the form [nodelist][layerlist] determined by the
    given sizes and intersections requirements. This corresponds to the nnodes
    and nlayers arguments of default_check_reqs. See Details section on how these
    are calculated.
    
    Parameters
    ----------
    sizes : list of ints > 0
        How many nodes should be on each layer of an acceptable induced subgraph.
        One integer for each layer of an acceptable subgraph.
    intersections : list of ints >= 0
        How many nodes should be shared between sets of layers in an acceptable
        induced subgraph. If an entry in the list is None, any number of shared
        nodes is accepted. The order of the intersections is taken to follow the
        order of layers in sizes, with two-layer intersections being listed first,
        then three-layer intersections, etc. For more details, see section
        "Constructing the requirements" in default_check_reqs docstring.
        
    Returns
    -------
    nnodes, nlayers : ints
        The number of nodes and the number of layers required of an acceptable subgraph,
        as determined by the sizes and intersections requirements.
        
    Details
    -------
    The number of layers (nlayers) that an acceptable subgraph must have is simply the
    length of sizes (since there is an entry for each layer). The number of nodes
    is the cardinality (size) of the union of the sets of nodes on each layer.
    This cardinality is unambiguously determined by the numbers of nodes on each
    layer (sizes) and the number of shared nodes between all combinations of
    layers (intersections), assuming that there are no undefined values (Nones)
    in intersections. The cardinality and thus nnodes is calculated by following
    the inclusion-exclusion principle.
    
    Example
    -------
    Calling
    
    >>> nnodes,nlayers = default_calculate_required_lengths([2,3,4],[2,1,2,1])
    
    returns nnodes = 5 and nlayers = 3, because
    nnodes = 2+3+4-2-1-2+1 and nlayers = len([2,3,4]) = 3. Therefore, an induced
    subgraph must have 5 nodes and 3 layers for it to be possible to satisfy the
    sizes and intersections requirements.
    """
    assert sizes != [], "Empty layer size list"
    assert len(intersections) == 2**len(sizes)-len(sizes)-1, "Wrong number of intersections"
    assert all(i>=1 and isinstance(i,int) for i in sizes) and all(j>=0 and isinstance(j,int) for j in intersections), "Inappropriate intersections or sizes"
    if not intersections:
        return sizes[0],1
    nlayers = len(sizes)
    nnodes = sum(sizes)
    index = 0
    for ii in range(2,len(sizes)+1):
        for _ in list(itertools.combinations(sizes,ii)):
            if ii % 2 == 0:
                nnodes = nnodes - intersections[index]
                index = index + 1
            else:
                nnodes = nnodes + intersections[index]
                index = index + 1
    return nnodes,nlayers
    
    
    
def relaxed_check_reqs(network,nodelist,layerlist):
    """Checks whether a multilayer induced subgraph of the form [nodelist][layerlist] is connected
    and does not contain any empty layers or nodes. Works on one-aspect multilayer networks.
    See section Details for more information.
    
    Parameters
    ----------
    network : MultilayerNetwork
        A one-aspect multilayer network containing the induced subgraph.
    nodelist : list of node names
        The nodes in the induced subgraph.
    layerlist : list of layer names
        The layers in the induced subgraph.
        
    Returns
    -------
    True if the induced subgraph is connected and does not contain empty layers
    or nodes, False otherwise.
    
    Details
    -------
    The phrase 'does not contain any empty layers or nodes' means that for each
    layer, there is at least one nodelayer in the induced subgraph, and that for
    each node, there is at least one nodelayer in the induced subgraph.
    In other words, each node in the nodelist and each layer in the layerlist
    appears at least once as the node identity or the layer identity, respectively,
    among the nodelayers present in the induced subgraph.
    
    Example
    -------
    Suppose we have the multilayer network N:
    
    (1,'X')----(2,'X')
                  |
                  |
               (2,'Y')
               
    Calling
    
    >>> relaxed_check_reqs(N,[1,2],['X','Y'])
    
    returns True, but calling
    
    >>> relaxed_check_reqs(N,[1,2],['Y'])
    
    returns False, because node 1 is empty.
    """
    induced_graph = pymnet.subnet(network,nodelist,layerlist)
    try:
        graph_is_connected = pymnet.nx.is_connected(pymnet.transforms.get_underlying_graph(induced_graph))
    except pymnet.nx.networkx.NetworkXPointlessConcept:
        return False
    if graph_is_connected:
        nls = set(induced_graph.iter_node_layers())
        for layer in layerlist:
            no_nodelayers = True
            for node in nodelist:
                if (node,layer) in nls:
                    no_nodelayers = False
                    break
            if no_nodelayers:
                return False
        for node in nodelist:
            no_nodelayers = True
            for layer in layerlist:
                if (node,layer) in nls:
                    no_nodelayers = False
                    break
            if no_nodelayers:
                return False
        return True
    return False      
