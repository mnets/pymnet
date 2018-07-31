# -*- coding: utf-8 -*-

import pymnet
from .reqs import default_check_reqs,default_calculate_required_lengths,relaxed_check_reqs
import random
import itertools

def sample_multilayer_subgraphs_esu(network,results,sizes=None,intersections=None,nnodes=None,nlayers=None,p=None,seed=None,intersection_type="strict",copy_network=True,custom_check_function=None):
    u"""A one-aspect multilayer version of the Rand-EnumerateSubgraphs (Rand-ESU) algorithm
    introduced by Wernicke [1].
    
    Uniformly samples induced subgraphs of the form [nodelist][layerlist] which
    fulfill the given requirements. Each subgraph is sampled at probability
    product(p), where p is the parameter p. If all entries in p are 1, all
    such induced subgraphs in the network are found.
    
    Parameters
    ----------
    Multiple parameters can be given by the user, some of which are always required,
    some of which are sometimes required, and some of which are mutually
    exclusive. There are multiple functionalities to this function, and the choice
    is done based on the parameters passed by the user. For a description of all
    of them, see section Usage.
    
    network : MultilayerNetwork
        The multilayer network to be analyzed.
    results : list or callable
        The method of outputting the found induced subgraphs. If a list, then
        the induced subgraphs are appended to it as ([nodelist],[layerlist]) tuples.
        The results list or the [nodelist] or [layerlist] lists are not guaranteed to
        be in any specific order.
        If a callable, when an acceptable induced subgraph is found, this callable
        is called with the argument ([nodelist],[layerlist]) (that is, one argument
        which is a tuple of two lists). The callable should therefore take only one
        required parameter in the form of a tuple. If you want to pass more parameters
        to the callable, do so via e.g. an anonymous function.
    sizes : list of ints > 0
        How many nodes should be on each layer of an acceptable induced subgraph.
        One integer for each layer of an acceptable subgraph.
    intersections : list of ints >= 0 or Nones, or int
        How many nodes should be shared between sets of layers in an acceptable
        induced subgraph. If list, if an entry in the list is None, any number of shared
        nodes is accepted. The order of the intersections is taken to follow the
        order of layers in sizes, with two-layer intersections being listed first,
        then three-layer intersections, etc. If int, then this is taken to mean
        the intersection between ALL layers, and the other intersections can be anything.
        If this is an int with value x, it is equivalent to being a list with
        [None,None,...,None,x].
        For more details, see section "Constructing the requirements" in the documentation
        of the function default_check_reqs.
    nnodes : int
        How many nodes an acceptable subgraph should have. If not provided and
        sizes and intersections are provided, it
        will be calculated based on the sizes and intersections parameters.
        Required if there are Nones in intersections or if intersection_type
        is not "strict". If you cannot guarantee the correctness of this
        number, do not use this parameter.
    nlayers : int
        How many layers an acceptable subgraph should have. If not provided and
        sizes and intersections are provided,
        it will be calculated based on the sizes and intersections requirements.
        If you cannot guarantee the correctness of this number, do not use this
        parameter.
    p : list of floats 0 <= p <= 1
        List of sampling probabilities at each depth. If None, p = 1 for each
        depth is used. The probability of sampling a given induced subgraph is
        the product of the elements of p.
        It is up to the user to provide a p of correct length to
        match the depth at which desired induced subgraphs are found.
        If you know how many nodes and layers an acceptable induced subgraph should
        have (nnodes and nlayers, respectively), you can calculate the length of p by:
        len(p) = nnodes - 1 + nlayers - 1 + 1.
        This formula follows from the fact that finding an induced subgraph starts
        from a nodelayer (the + 1), and then each node and each layer have to be added
        one at a time to the nodelist and layerlist, respectively
        (nnodes - 1 and nlayers - 1, respectively). Starting from a nodelayer means
        that both nodelist and layerlist are of length 1 when the expansion of the
        subgraph is started, hence the - 1's.
    seed : int, str, bytes or bytearray
        Seed for Rand-ESU.
    intersection_type : string, "strict" or "less_or_equal"
        If intersection_type is "strict", all intersections must be exactly equal
        to entries in the intersections parameter. If intersection_type is
        "less_or_equal", an intersection is allowed to be less than or equal to the corresponding
        entry in the intersections parameter. Usage is case-sensitive.
    copy_network : boolean
        Determines whether the network is copied at the beginning of execution. If True (default),
        the network is copied and the copy is modified during the execution (the original
        network is not modified). If False, the network is not copied, and the network is
        NOT modified during the execution.
        The copying takes more memory but results in faster execution times - the default
        value (True) is the recommended setting. The modification of the copy does not affect
        the edges in the induced subgraphs that are passed to the check function. During the
        execution, if this parameter is True, as starting nodelayers are iterated through in their numerical order,
        after a nodelayer has been iterated over all edges leading to it are removed (at this
        point, it is impossible to reach the nodelayer from subsequent starting nodelayers in
        any case). Therefore, if you use a custom_check_function whose return value depends
        also on the edges OUTSIDE the induced subgraph to be tested, set this parameter to False.
    custom_check_function : callable or None
        If not None, this will be used to determine whether an induced subgraph is okay or not
        (instead of one of the built-in check functions).
        The algorithm finds induced subgraphs which have the given nnodes and nlayers, and which
        have a path spanning the induced subgraph (but are not necessarily connected). The algorithm
        then passes these to the check function, which determines whether the subgraph is acceptable
        or not. The arguments that are passed to your custom check function are the network, the nodelist
        of the induced subgraph, and the layerlist of the induced subgraph (three parameters, in this
        order). Your check function should therefore accept exactly three parameters. If you want to pass
        more parameters to the check function, do so via e.g. an anonymous function.
        If copy_network is True, the passed network is the copy of the network, which might have
        edges removed OUTSIDE of the induced subgraph (the edges inside the induced subgraph are identical
        to the original network's). The function should return True or False (the subgraph is acceptable
        or not acceptable, respectively). When this parameter is not None, you must also specify nnodes
        and nlayers.
        
    Usage
    -----
    There are multiple functionalities built-in, and determining which is used is
    done by checking which parameters have been given by the user.
    
    If you want to find induced subgraphs (ISs) that have a specified number of nodes
    on each layer and have specific intersections between layers, provide:
        - network
        - results
        - sizes
        - intersections as list without Nones
        
    If you want to find ISs that have a specific number of nodes on each layer and
    have some specific intersections between layers, and some intersections that can
    be of any cardinality, provide:
        - network
        - results
        - sizes
        - intersections as list with Nones in the elements where intersection cardinalities can be anything (even all elements can be Nones)
        - nnodes
        
    If you want to find ISs that have a specific number of nodes on each layer and
    have intersections that have at most specific cardinalities, provide:
        - network
        - results
        - sizes
        - intersections as list without Nones
        - nnodes
        - intersection_type = "less_or_equal"
        
    If you want to find ISs that have a specific number of nodes on each layer and
    have some specific intersections that have at most specific cardinalities, and some
    intersections that can be of any cardinality, provide:
        - network
        - results
        - sizes
        - intersections as list with Nones in the elements where intersection cardinalities can be anything (even all intersections can be Nones)
        - nnodes
        - intersection_type = "less_or_equal"
        
    If you want to find ISs that have a specific number of nodes on each layer and
    have a specific intersection between ALL layers (the other intersections can be anything),
    provide:
        - network
        - results
        - sizes
        - nnodes
        - intersections as int
        
    If you want to find ISs that have a specific number of nodes and a specific number
    of layers, provide:
        - network
        - results
        - nnodes
        - nlayers
        
    If you want to define your own function to determine when an IS is acceptable,
    provide:
        - network
        - results
        - nnodes
        - nlayers
        - custom_check_function
    
    For all of the above uses, if you don't want to find all ISs but only sample a
    portion of them, also provide:
        - p
    
    Of the above uses, the first five use the default_check_reqs function for checking
    subgraph validity, the sixth uses the relaxed_check_reqs function, and the seventh
    uses the user-supplied checking function.
    
    Example
    -------
    Suppose we have the multilayer network N:
    
    (1,'X')----(2,'X')----(3,'X')
                  |
                  |
               (2,'Y')
    
    where (a,b) are nodelayer tuples with a = node identity and b = layer identity.
    After calling
    
    >>> results = []
    >>> sample_multilayer_subgraphs_esu(N,results,[2,1],[1])
    
    the results list looks like [([1,2],['X','Y']),([2,3],['X','Y'])] (or some other
    order of tuples and [nodelist] and [layerlist] inside the tuples, since the output
    is not guaranteed to be in any specific order).
    
    After calling
    
    >>> results = []
    >>> sample_multilayer_subgraphs_esu(N,results,nnodes=3,nlayers=1)
    
    the results list looks like [([1,2,3],['X'])] (or again, some other ordering).
    
    Further reading
    ---------------
    The documentation of the functions default_check_reqs, default_calculate_required_lengths
    and relaxed_check_reqs offer more insight into what are considered acceptable induced subgraphs
    in different cases in the functionalities described in the Usage section. You should read these
    if you are not sure what you want to do or how to do it after reading this documentation.
    
    References
    ----------
    [1] "A Faster Algorithm for Detecting Network Motifs", S. Wernicke, WABI. Vol. 3692, pp. 165-177. Springer 2005.
    """
    if copy_network == True:
        network_copy = pymnet.subnet(network,network.get_layers(aspect=0),network.get_layers(aspect=1),newNet=pymnet.MultilayerNetwork(aspects=1,fullyInterconnected=False))
    else:
        network_copy = network
        
    if seed == None:
        random.seed()
    else:
        random.seed(seed)

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
        
    if p == None:
        p = [1] * (req_nodelist_len-1 + req_layerlist_len-1 + 1)
        
    depth = 0
    numberings = dict()
    inverse_numberings = dict()
    for index,nodelayer in enumerate(network_copy.iter_node_layers()):
        numberings[nodelayer] = index
    for nodelayer in numberings:
        inverse_numberings[numberings[nodelayer]] = nodelayer

    for indexnumber in range(len(numberings)):
        v = inverse_numberings[indexnumber]
        if random.random() < p[depth]:
            start_node = v[0]
            start_layer = v[1]
            V_extension_nodes = set()
            V_extension_layers = set()
            for neighbor in network_copy[v]:
                if numberings[neighbor] > numberings[v]:
                    no_node_conflicts = True
                    no_layer_conflicts = True
                    node = neighbor[0]
                    layer = neighbor[1]
                    if (node,start_layer) in numberings and numberings[(node,start_layer)] < numberings[v]:
                        no_node_conflicts = False
                    if (start_node,layer) in numberings and numberings[(start_node,layer)] < numberings[v]:
                        no_layer_conflicts = False
                    if (node != start_node
                        and no_node_conflicts
                        and node not in V_extension_nodes):
                        V_extension_nodes.add(node)
                    if (layer != start_layer
                        and no_layer_conflicts
                        and layer not in V_extension_layers):
                        V_extension_layers.add(layer)
            _extend_subgraph(network_copy,[start_node],[start_layer],check_function,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,depth+1,p,results)
        if copy_network == True:
            for neighbor in list(network_copy[v]):
                network_copy[neighbor][v] = 0

def _extend_subgraph(network,nodelist,layerlist,check_function,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,depth,p,results):    
    # A helper function of sample_multilayer_subgraphs_esu, not intended for use by users    
    if len(nodelist) > req_nodelist_len or len(layerlist) > req_layerlist_len:
        return
    if len(nodelist) == req_nodelist_len and len(layerlist) == req_layerlist_len:
        if check_function(network,nodelist,layerlist):
            if isinstance(results,list):
                results.append((list(nodelist),list(layerlist)))
                return
            elif callable(results):
                results((list(nodelist),list(layerlist)))
                return
            else:
                raise TypeError("Please provide results container as list or callable")
        else:
            return
    if len(nodelist) == req_nodelist_len:
        V_extension_nodes = set()
    
    # Calculate the original neighborhood
    orig_graph = set(nl for nl in itertools.product(nodelist,layerlist) if nl in numberings)
    orig_neighborhood_nodelist = set()
    orig_neighborhood_layerlist = set()
    for nodelayer in orig_graph:
                for neighbor in network[nodelayer]:
                    if neighbor[0] not in nodelist and neighbor[0] not in orig_neighborhood_nodelist and numberings[neighbor] > numberings[v]:
                        orig_neighborhood_nodelist.add(neighbor[0])
                    if neighbor[1] not in layerlist and neighbor[1] not in orig_neighborhood_layerlist and numberings[neighbor] > numberings[v]:
                        orig_neighborhood_layerlist.add(neighbor[1])
    
    while V_extension_nodes or V_extension_layers:
        new_nodelist = list(nodelist)
        new_layerlist = list(layerlist)
        node_added = None
        layer_added = None
        if V_extension_nodes:
            node_added = V_extension_nodes.pop()
            new_nodelist.append(node_added)
        else:
            layer_added = V_extension_layers.pop()
            new_layerlist.append(layer_added)
        if random.random() < p[depth]:
            if node_added != None:
                added_graph = [nl for nl in itertools.product([node_added],new_layerlist) if nl in numberings]
            elif layer_added != None:
                added_graph = [nl for nl in itertools.product(new_nodelist,[layer_added]) if nl in numberings]
            V_extension_nodes_prime = set(V_extension_nodes)
            V_extension_layers_prime = set(V_extension_layers)
            for nodelayer in added_graph:
                for neighbor in network[nodelayer]:
                    if numberings[neighbor] > numberings[v]:
                        no_node_conflicts = True
                        no_layer_conflicts = True
                        node = neighbor[0]
                        layer = neighbor[1]
                        if (node not in orig_neighborhood_nodelist
                            and node not in V_extension_nodes_prime
                            and node not in new_nodelist):
                            for nl in itertools.product([node],new_layerlist):
                                if nl in numberings and numberings[nl] < numberings[v]:
                                    no_node_conflicts = False
                            if no_node_conflicts:
                                V_extension_nodes_prime.add(node)
                        if (layer not in orig_neighborhood_layerlist
                            and layer not in V_extension_layers_prime
                            and layer not in new_layerlist):
                            for nl in itertools.product(new_nodelist,[layer]):
                                if nl in numberings and numberings[nl] < numberings[v]:
                                    no_layer_conflicts = False
                            if no_layer_conflicts:
                                V_extension_layers_prime.add(layer)

            _extend_subgraph(network,new_nodelist,new_layerlist,check_function,V_extension_nodes_prime,V_extension_layers_prime,numberings,v,req_nodelist_len,req_layerlist_len,depth+1,p,results)    
    return   