# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import pymnet
from reqs import check_reqs,calculate_required_lengths
import random

def enumerateSubgraphs(network,sizes,intersections,resultlist,p=None,seed=None):
    """The multilayer version of the ESU algorithm. Uniformly samples induced subgraphs
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
        are in the same order as in sizes.
    resultlist : list
        Where found induced subgraphs are appended as tuples (nodelist, layerlist).
    p : list of floats 0 <= p <= 1
        List of sampling probabilities at each depth. If None, p = 1 for each
        depth is used.
    
    TODO: listat pois
    parempi naapuruston ja node conflictien checkki! Miksi set[neighbor]?
    mieti verkon kopiointi ja nl:ien poisto
    seed parametriksi
    """
    if seed == None:
        random.seed()
    else:
        random.seed(seed)
    depth = 0
    numberings = dict()
    for index,nodelayer in enumerate(network.iter_node_layers()):
        numberings[nodelayer] = index
    req_nodelist_len,req_layerlist_len = calculate_required_lengths(sizes,intersections)
    if p == None:
        p = [1] * (req_nodelist_len-1 + req_layerlist_len-1 + 1)    
    for v in numberings:
        if random.random() < p[depth]:
            nodelist = [v[0]]
            layerlist = [v[1]]
            V_extension_nodes = []
            V_extension_layers = []
            for neighbor in network[v]:
                no_node_conflicts = True
                no_layer_conflicts = True
                node = neighbor[0]
                layer = neighbor[1]
                #for nl in itertools.chain(pymnet.subnet(...).iter_node_layers(),(neighbor)):
                for nl in set(pymnet.subnet(network,[node],layerlist).iter_node_layers()) | set([neighbor]):
                    if numberings[nl] < numberings[v]:
                        no_node_conflicts = False
                for nl in set(pymnet.subnet(network,nodelist,[layer]).iter_node_layers()) | set([neighbor]):
                    if numberings[nl] < numberings[v]:
                        no_layer_conflicts = False
                if (node not in nodelist
                    and no_node_conflicts
                    and node not in V_extension_nodes):
                    V_extension_nodes.append(node)
                if (layer not in layerlist
                    and no_layer_conflicts
                    and layer not in V_extension_layers):
                    V_extension_layers.append(layer)
            _extendSubgraph(network,nodelist,layerlist,sizes,intersections,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,depth+1,p,resultlist)
        

def _extendSubgraph(network,nodelist,layerlist,sizes,intersections,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,depth,p,resultlist):    
    if len(nodelist) > req_nodelist_len or len(layerlist) > req_layerlist_len:
        return
    if len(nodelist) == req_nodelist_len and len(layerlist) == req_layerlist_len:
        try:
            if check_reqs(network,nodelist,layerlist,sizes,intersections,(req_nodelist_len,req_layerlist_len)):
                resultlist.append((list(nodelist),list(layerlist)))
                return
            else:
                return
        except AssertionError:
            pass
    while V_extension_nodes or V_extension_layers:
        new_nodelist = list(nodelist)
        new_layerlist = list(layerlist)
        if V_extension_nodes:
            new_nodelist.append(V_extension_nodes.pop())
        else:
            new_layerlist.append(V_extension_layers.pop())
        if random.random() < p[depth]:
            induced_graph = set(pymnet.subnet(network,new_nodelist,new_layerlist).iter_node_layers())
            orig_graph = set(pymnet.subnet(network,nodelist,layerlist).iter_node_layers())
            added_graph = [nl for nl in induced_graph if nl not in orig_graph]
            orig_neighborhood_nodelist = set()
            orig_neighborhood_layerlist = set()
            for nodelayer in orig_graph:
                for neighbor in network[nodelayer]:
                    if neighbor[0] not in nodelist and neighbor[0] not in orig_neighborhood_nodelist and numberings[neighbor] > numberings[v]:
                        orig_neighborhood_nodelist.add(neighbor[0])
                    if neighbor[1] not in layerlist and neighbor[1] not in orig_neighborhood_layerlist and numberings[neighbor] > numberings[v]:
                        orig_neighborhood_layerlist.add(neighbor[1])
            V_extension_nodes_prime = list(V_extension_nodes)
            V_extension_layers_prime = list(V_extension_layers)
            for nodelayer in added_graph:
                for neighbor in network[nodelayer]:
                    if numberings[neighbor] > numberings[v]:
                        no_node_conflicts = True
                        no_layer_conflicts = True
                        node = neighbor[0]
                        layer = neighbor[1]
                        for nl in set(pymnet.subnet(network,[node],new_layerlist).iter_node_layers()) | set([neighbor]):
                            if numberings[nl] < numberings[v]:
                                no_node_conflicts = False
                        for nl in set(pymnet.subnet(network,new_nodelist,[layer]).iter_node_layers()) | set([neighbor]):
                            if numberings[nl] < numberings[v]:
                                no_layer_conflicts = False
                        if (node not in orig_neighborhood_nodelist 
                            and node not in new_nodelist 
                            and no_node_conflicts
                            and node not in V_extension_nodes_prime):
                            V_extension_nodes_prime.append(node)
                        if (layer not in orig_neighborhood_layerlist 
                            and layer not in new_layerlist 
                            and no_layer_conflicts 
                            and layer not in V_extension_layers_prime):
                            V_extension_layers_prime.append(layer)
            _extendSubgraph(network,new_nodelist,new_layerlist,sizes,intersections,V_extension_nodes_prime,V_extension_layers_prime,numberings,v,req_nodelist_len,req_layerlist_len,depth+1,p,resultlist)    
    return
        

                
                
                
                
                
                
                
                
                
                
                
    
    