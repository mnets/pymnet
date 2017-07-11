# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import pymnet
from reqs import check_reqs,calculate_required_lengths
import random
import itertools

def enumerateSubgraphs(network,sizes,intersections,resultlist,p=None,seed=None):
    u"""The multilayer version of the ESU algorithm. Uniformly samples induced subgraphs
    of the form [nodelist][layerlist], which fulfill the given requirements.
    
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
    p : list of floats 0 <= p <= 1
        List of sampling probabilities at each depth. If None, p = 1 for each
        depth is used.
    seed : int, str, bytes or bytearray
        Seed for Rand-ESU
        
    TODO: listat pois
    parempi naapuruston ja node conflictien checkki
    mieti verkon kopiointi ja nl:ien poisto
    kayttajan maarittelema check-funktio
    tilastollinen testaus että samplaus toimii kuten pitaa
    """
    network_copy = pymnet.subnet(network,network.get_layers(aspect=0),network.get_layers(aspect=1),newNet=pymnet.MultilayerNetwork(aspects=1,fullyInterconnected=False))
    if seed == None:
        random.seed()
    else:
        random.seed(seed)
    depth = 0
    numberings = dict()
    inverse_numberings = dict()
    for index,nodelayer in enumerate(network_copy.iter_node_layers()):
        numberings[nodelayer] = index
    for nodelayer in numberings:
        inverse_numberings[numberings[nodelayer]] = nodelayer
    req_nodelist_len,req_layerlist_len = calculate_required_lengths(sizes,intersections)
    if p == None:
        p = [1] * (req_nodelist_len-1 + req_layerlist_len-1 + 1)
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
            _extendSubgraph(network_copy,[start_node],[start_layer],sizes,intersections,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,depth+1,p,resultlist)
        for neighbor in list(network_copy[v]):
            network_copy[neighbor][v] = 0

def _extendSubgraph(network,nodelist,layerlist,sizes,intersections,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,depth,p,resultlist):    
    if len(nodelist) > req_nodelist_len or len(layerlist) > req_layerlist_len:
        return
    if len(nodelist) == req_nodelist_len and len(layerlist) == req_layerlist_len:
        if check_reqs(network,nodelist,layerlist,sizes,intersections,(req_nodelist_len,req_layerlist_len)):
            resultlist.append((list(nodelist),list(layerlist)))
            return
        else:
            return
    if len(nodelist) == req_nodelist_len:
        V_extension_nodes = set()
    
    # Calculate the original neighborhood
    #orig_graph = set(pymnet.subnet(network,nodelist,layerlist).iter_node_layers())
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
            #induced_graph = set(pymnet.subnet(network,new_nodelist,new_layerlist).iter_node_layers())
            #orig_graph = set(pymnet.subnet(network,nodelist,layerlist).iter_node_layers())
            #added_graph = [nl for nl in induced_graph if nl not in orig_graph]
            #orig_neighborhood_nodelist = set()
            #orig_neighborhood_layerlist = set()
            #for nodelayer in orig_graph:
            #    for neighbor in network[nodelayer]:
            #        if neighbor[0] not in nodelist and neighbor[0] not in orig_neighborhood_nodelist and numberings[neighbor] > numberings[v]:
            #            orig_neighborhood_nodelist.add(neighbor[0])
            #        if neighbor[1] not in layerlist and neighbor[1] not in orig_neighborhood_layerlist and numberings[neighbor] > numberings[v]:
            #            orig_neighborhood_layerlist.add(neighbor[1])
            V_extension_nodes_prime = set(V_extension_nodes)
            V_extension_layers_prime = set(V_extension_layers)
            for nodelayer in added_graph:
                for neighbor in network[nodelayer]:
                    if numberings[neighbor] > numberings[v]:
                        no_node_conflicts = True
                        no_layer_conflicts = True
                        node = neighbor[0]
                        layer = neighbor[1]
                        for nl in pymnet.subnet(network,[node],new_layerlist).iter_node_layers():
                            if numberings[nl] < numberings[v]:
                                no_node_conflicts = False
                        for nl in pymnet.subnet(network,new_nodelist,[layer]).iter_node_layers():
                            if numberings[nl] < numberings[v]:
                                no_layer_conflicts = False
                        if (node not in orig_neighborhood_nodelist 
                            and node not in new_nodelist 
                            and no_node_conflicts
                            and node not in V_extension_nodes_prime):
                            V_extension_nodes_prime.add(node)
                        if (layer not in orig_neighborhood_layerlist 
                            and layer not in new_layerlist 
                            and no_layer_conflicts 
                            and layer not in V_extension_layers_prime):
                            V_extension_layers_prime.add(layer)
            _extendSubgraph(network,new_nodelist,new_layerlist,sizes,intersections,V_extension_nodes_prime,V_extension_layers_prime,numberings,v,req_nodelist_len,req_layerlist_len,depth+1,p,resultlist)    
    return
        

                
                
                
                
                
                
                
                
                
                
                
    
    