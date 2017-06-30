# -*- coding: utf-8 -*-
"""
@author: T. Nurmi
"""

import pymnet
from pymnet import nx
import PyBliss
#import matplotlib.pyplot as plt
from reqs import check_reqs,calculate_required_lengths
#import itertools
import pdb

'''
def enumerateSubgraphs(network,sizes,intersections):    
    numberings = dict()
    for index,nodelayer in enumerate(list(network.iter_node_layers())):
        numberings[nodelayer] = index
        
    #print(numberings)
        
    req_nodelist_len, req_layerlist_len = calculate_required_lengths(sizes,intersections)
        
    for v in numberings:
        nodelist = [v[0]]
        layerlist = [v[1]]
        V_extension = []
        for neighbor in list(network[v]):
            if neighbor[0] != v[0] and neighbor[1] != v[1]:
                no_conflicts = True
                for nodelayer in list(pymnet.subnet(network,[v[0],neighbor[0]],[v[1],neighbor[1]]).iter_node_layers()):
                    if nodelayer != v and numberings[nodelayer] < numberings[v]:
                        no_conflicts = False
                if no_conflicts:
                    V_extension.append(neighbor)
            elif numberings[neighbor] > numberings[v]:
                V_extension.append(neighbor)
        extendSubgraph_v2(network,nodelist,layerlist,sizes,intersections,V_extension,numberings,v,req_nodelist_len,req_layerlist_len,depth=0)
'''

def enumerateSubgraphs_v3(network,sizes,intersections,resultlist):
    numberings = dict()
    for index,nodelayer in enumerate(list(network.iter_node_layers())):
        numberings[nodelayer] = index
    req_nodelist_len,req_layerlist_len = calculate_required_lengths(sizes,intersections)
    for v in numberings:
        nodelist = [v[0]]
        layerlist = [v[1]]
        V_extension_nodes = []
        V_extension_layers = []
        for neighbor in list(network[v]):
            no_node_conflicts = True
            no_layer_conflicts = True
            node = neighbor[0]
            layer = neighbor[1]
            for nl in list(set(pymnet.subnet(network,[node],layerlist).iter_node_layers()) | set([neighbor])):
                if numberings[nl] < numberings[v]:
                    no_node_conflicts = False
            for nl in list(set(pymnet.subnet(network,nodelist,[layer]).iter_node_layers()) | set([neighbor])):
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
        extendSubgraph_v4(network,nodelist,layerlist,sizes,intersections,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,0,resultlist)
'''
def enumerateSubgraphs_v2(network,sizes,intersections,resultlist):
    numberings = dict()
    for index,nodelayer in enumerate(list(network.iter_node_layers())):
        numberings[nodelayer] = index
        
    print(numberings)
    #pdb.set_trace()
    req_nodelist_len, req_layerlist_len = calculate_required_lengths(sizes,intersections)
    
    for v in numberings:
        nodelist = [v[0]]
        layerlist = [v[1]]
        allowed_neighbors = []
        V_extension_nodes = []
        V_extension_layers = []
        for neighbor in list(network[v]):
            if neighbor[0] != v[0] and neighbor[1] != v[1]:
                no_conflicts = True
                for nodelayer in list(pymnet.subnet(network,[v[0],neighbor[0]],[v[1],neighbor[1]]).iter_node_layers()):
                    if nodelayer != v and numberings[nodelayer] < numberings[v]:
                        no_conflicts = False
                if no_conflicts:
                    allowed_neighbors.append(neighbor)
            elif numberings[neighbor] > numberings[v]:
                allowed_neighbors.append(neighbor)
        #print('all_neigh:',allowed_neighbors)
        for nodelayer in allowed_neighbors:
            if nodelayer[0] not in V_extension_nodes and nodelayer[0] not in nodelist:
                V_extension_nodes.append(nodelayer[0])
            if nodelayer[1] not in V_extension_layers and nodelayer[1] not in layerlist:
                V_extension_layers.append(nodelayer[1])
        extendSubgraph_v4(network,nodelist,layerlist,sizes,intersections,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,0,resultlist)
'''
def extendSubgraph_v4(network,nodelist,layerlist,sizes,intersections,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,depth,resultlist):
    #if 21 in nodelist and 1 in layerlist:
        #print('start:',nodelist,layerlist,'V_exts:',V_extension_nodes,V_extension_layers,'depth:',depth)    
    if len(nodelist) > req_nodelist_len or len(layerlist) > req_layerlist_len:
        return
    try:
        if check_reqs(network,nodelist,layerlist,sizes,intersections,(req_nodelist_len,req_layerlist_len)):
            #print('ESU:',(list(nodelist),list(layerlist)))
            resultlist.append((list(nodelist),list(layerlist)))
            return
    except AssertionError:
        pass
    while V_extension_nodes or V_extension_layers:
        new_nodelist = nodelist[:]
        new_layerlist = layerlist[:]
        if V_extension_nodes:
            new_nodelist.append(V_extension_nodes.pop())
        else:
            new_layerlist.append(V_extension_layers.pop())
        induced_graph = list(pymnet.subnet(network,new_nodelist,new_layerlist).iter_node_layers())
        orig_graph = list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers())
        added_graph = [nl for nl in induced_graph if nl not in orig_graph]
        orig_neighborhood_nodelist = []
        orig_neighborhood_layerlist = []
        #if 21 in nodelist and 1 in layerlist:
            #print('orig, ind and added:',orig_graph,induced_graph,added_graph)
        for nodelayer in orig_graph:
            for neighbor in list(network[nodelayer]):
                if neighbor[0] not in nodelist and neighbor[0] not in orig_neighborhood_nodelist and numberings[neighbor] > numberings[v]:
                    orig_neighborhood_nodelist.append(neighbor[0])
                if neighbor[1] not in layerlist and neighbor[1] not in orig_neighborhood_layerlist and numberings[neighbor] > numberings[v]:
                    orig_neighborhood_layerlist.append(neighbor[1])
        #if 21 in nodelist and 1 in layerlist:
            #print('neighborhood lists:',orig_neighborhood_nodelist,orig_neighborhood_layerlist)
        V_extension_nodes_prime = V_extension_nodes[:]
        V_extension_layers_prime = V_extension_layers[:]
        for nodelayer in added_graph:
            for neighbor in list(network[nodelayer]):
                if numberings[neighbor] > numberings[v]:
                    no_node_conflicts = True
                    no_layer_conflicts = True
                    node = neighbor[0]
                    layer = neighbor[1]
                    for nl in list(set(pymnet.subnet(network,[node],new_layerlist).iter_node_layers()) | set([neighbor])):
                        if numberings[nl] < numberings[v]:
                            no_node_conflicts = False
                    for nl in list(set(pymnet.subnet(network,new_nodelist,[layer]).iter_node_layers()) | set([neighbor])):
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
        #if 21 in nodelist and 1 in layerlist:
            #print('newlists:',new_nodelist,new_layerlist,'extensions:',V_extension_nodes_prime,V_extension_layers_prime)
        extendSubgraph_v4(network,new_nodelist,new_layerlist,sizes,intersections,V_extension_nodes_prime,V_extension_layers_prime,numberings,v,req_nodelist_len,req_layerlist_len,depth+1,resultlist)    
    return
        
def extendSubgraph_v3(network,nodelist,layerlist,sizes,intersections,V_extension_nodes,V_extension_layers,numberings,v,req_nodelist_len,req_layerlist_len,depth,resultlist):
    print('start lists:',nodelist,layerlist,'V_ext:',V_extension_nodes,V_extension_layers,'depth:',depth)
    if len(nodelist) > req_nodelist_len or len(layerlist) > req_layerlist_len:
        return # try if this works, there's prob some other problem
        # the result shouldn't be appended if it's the wrong length!!! what's going on with the checker?
    try:
        if check_reqs(network,nodelist,layerlist,sizes,intersections):
            print('esu',nodelist,layerlist,'depth:',depth)
            resultlist.append((list(nodelist),list(layerlist)))
            #pdb.set_trace()
            return
    except AssertionError:
        pass
    while V_extension_nodes or V_extension_layers:
        new_nodelist = nodelist[:]
        new_layerlist = layerlist[:]
        if V_extension_nodes:
            new_nodelist.append(V_extension_nodes.pop())
        else:
            new_layerlist.append(V_extension_layers.pop())
        induced_graph = list(pymnet.subnet(network,new_nodelist,new_layerlist).iter_node_layers())
        orig_graph = list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers())
        added_graph = [nl for nl in induced_graph if nl not in orig_graph]
        #V_extension = [nl for nl in V_extension if nl not in induced_graph]
        orig_neighborhood = []
        for nl in list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers()):
            for neighbor in list(network[nl]):
                if neighbor not in orig_neighborhood and neighbor not in list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers()):
                    orig_neighborhood.append(neighbor)
        V_extension_nodes_prime = V_extension_nodes[:]
        V_extension_layers_prime = V_extension_layers[:]
        extension = []
        for nodelayer in added_graph:
            for neighbor in list(network[nodelayer]):
                no_conflicts = True
                for nl in list(set(pymnet.subnet(network,[neighbor[0]],new_layerlist).iter_node_layers()) | set(pymnet.subnet(network,new_nodelist,[neighbor[1]]).iter_node_layers()) | set([neighbor])):
                    if numberings[nl] < numberings[v]:
                        no_conflicts = False
                if (neighbor not in orig_neighborhood and
                neighbor not in orig_graph and 
                no_conflicts and 
                numberings[neighbor] > numberings[v] and 
                neighbor not in extension):
                    extension.append(neighbor)
        for nodelayer in extension:
            if nodelayer[0] not in V_extension_nodes_prime and nodelayer[0] not in new_nodelist:
                V_extension_nodes_prime.append(nodelayer[0])
            if nodelayer[1] not in V_extension_layers_prime and nodelayer[1] not in new_layerlist:
                V_extension_layers_prime.append(nodelayer[1])
        print(new_nodelist,new_layerlist,'Extensions:',V_extension_nodes_prime,V_extension_layers_prime,)
        extendSubgraph_v3(network,new_nodelist,new_layerlist,sizes,intersections,V_extension_nodes_prime,V_extension_layers_prime,numberings,v,req_nodelist_len,req_layerlist_len,depth+1,resultlist)
    return
       
def extendSubgraph_v2(network,nodelist,layerlist,sizes,intersections,V_extension,numberings,v,req_nodelist_len,req_layerlist_len,depth):
    print(nodelist,layerlist,V_extension,depth)
    try:
        if check_reqs(network,nodelist,layerlist,sizes,intersections):
            print('esu',v,nodelist,layerlist,depth)
            #pdb.set_trace()
            return
    except AssertionError:
        pass
    if len(nodelist) > req_nodelist_len or len(layerlist) > req_layerlist_len:
        return
    while V_extension:
        print('V_extension',V_extension)        
        new_nodelist = nodelist[:]
        new_layerlist = layerlist[:]
        next_nodelayer = V_extension.pop()
        if next_nodelayer[0] not in new_nodelist:
            new_nodelist.append(next_nodelayer[0])
        if next_nodelayer[1] not in new_layerlist:
            new_layerlist.append(next_nodelayer[1])
        induced_graph = list(pymnet.subnet(network,new_nodelist,new_layerlist).iter_node_layers())
        orig_graph = list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers())
        added_graph = [nl for nl in induced_graph if nl not in orig_graph]
        V_extension = [nl for nl in V_extension if nl not in induced_graph]
        orig_neighborhood = []
        for nl in list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers()):
            for neighbor in list(network[nl]):
                if neighbor not in orig_neighborhood and neighbor not in list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers()):
                    orig_neighborhood.append(neighbor)
        V_extension_prime = V_extension[:]
        for nodelayer in added_graph:
            for neighbor in list(network[nodelayer]):
                no_conflicts = True
                for nl in list(set(pymnet.subnet(network,[neighbor[0]],new_layerlist).iter_node_layers()) | set(pymnet.subnet(network,new_nodelist,[neighbor[1]]).iter_node_layers()) | set([neighbor])):
                    if numberings[nl] < numberings[v]:
                        no_conflicts = False # Tarkista logiikka! Kaikki nodet jotka naapurin lisääminen tuo verkkoon (tuntuu oikealta)
                if (neighbor not in orig_neighborhood and
                neighbor not in orig_graph and 
                no_conflicts and 
                numberings[neighbor] > numberings[v] and 
                neighbor not in V_extension_prime):
                    V_extension_prime.append(neighbor)
        #print(next_nodelayer)
        extendSubgraph_v2(network,new_nodelist,new_layerlist,sizes,intersections,V_extension_prime,numberings,v,req_nodelist_len,req_layerlist_len,depth+1)
    return
        
def extendSubgraph(network,nodelist,layerlist,sizes,intersections,V_extension,numberings,v,req_nodelist_len,req_layerlist_len):
    #print('n+l:',nodelist,layerlist,V_extension)
    try:
        if check_reqs(network,nodelist,layerlist,sizes,intersections):
            print('esu',nodelist,layerlist)
            return
    except AssertionError:
        pass
    
    if len(nodelist) > req_nodelist_len or len(layerlist) > req_layerlist_len:
        return
        
        
        
    
    while V_extension:
        new_nodelist = nodelist[:]
        new_layerlist = layerlist[:]
        
        next_nodelayer = V_extension.pop()
        
        #print('next_nodelayer',next_nodelayer)
        
        node_added = False
        layer_added = False
        #print('v-e:',V_extension)
        if next_nodelayer[0] not in new_nodelist:
            node_added = True
            new_nodelist.append(next_nodelayer[0])
        if next_nodelayer[1] not in new_layerlist:
            layer_added = True
            new_layerlist.append(next_nodelayer[1])
        '''
        new_V_ext = []
        for element in V_extension:
            if not (element[0] in new_nodelist and element[1] in new_layerlist):
                new_V_ext.append(element)
        #new_V_ext = [entry for entry in V_extension if (entry[0] in new_nodelist and entry[1] in new_layerlist)]
        V_extension = new_V_ext[:]
        '''
                
        #print('Vext_new:',V_extension)
        
        induced_graph = list(pymnet.subnet(network,new_nodelist,new_layerlist).iter_node_layers())
        #print('newnodeandlayer:',new_nodelist,new_layerlist)
        #print('inducedgraph:',induced_graph)
        added_graph = list(pymnet.subnet(network,[next_nodelayer[0]],[next_nodelayer[1]]).iter_node_layers()) # ONLY GIVES ONE NL !!!
        orig_subgraph_neighborhood = []
        for nl in list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers()):
            for nb in list(network[nl]):
                if nb not in orig_subgraph_neighborhood and nb not in induced_graph:
                    orig_subgraph_neighborhood.append(nb)
        
        V_extension_prime = V_extension[:]
        for nodelayer in added_graph:
            for neighbor in list(network[nodelayer]):
                if (numberings[neighbor] > numberings[v] and
                neighbor not in V_extension_prime and
                neighbor not in induced_graph and
                neighbor not in orig_subgraph_neighborhood):
                    V_extension_prime.append(neighbor)
                    
        #print('Vprime',V_extension_prime)
        
        '''
        existing_neighborhood = []
        for nodelayer in list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers()):
            for neighbor in list(network[nodelayer]):
                if neighbor not in list(pymnet.subnet(network,nodelist,layerlist).iter_node_layers()) and neighbor not in existing_neighborhood:
                    existing_neighborhood.append(neighbor)
        
        added_neighborhood = []     
        for nodelayer in added_graph:
            for neighbor in list(network[nodelayer]):
                if (numberings[neighbor] > numberings[v] and
                neighbor not in existing_neighborhood and
                neighbor not in added_neighborhood):
                    added_neighborhood.append(neighbor)
                    
        V_extension_prime = list(set(V_extension) | set(added_neighborhood))
        print(V_extension_prime)
                    
        '''
        '''
        V_extension_prime = []
        for nodelayer in induced_graph:
            for neighbor in list(network[nodelayer]):
                if (numberings[neighbor] > numberings[v] and 
                neighbor not in induced_graph and 
                neighbor not in V_extension_prime):
                    V_extension_prime.append(neighbor)
        '''
            
        extendSubgraph(network,new_nodelist,new_layerlist,sizes,intersections,V_extension_prime,numberings,v,req_nodelist_len,req_layerlist_len)
    return
        
        
'''        
def calculate_required_lengths(sizes,intersections):
    if not intersections:
        return 1,0
    layerlist_length = len(sizes)
    nodelist_length = sum(sizes)
    index = 0
    for ii in range(2,len(sizes)+1):
        for jj,combination in enumerate(list(itertools.combinations(sizes,ii))):
            if ii % 2 == 0:
                nodelist_length = nodelist_length - intersections[index]
                index = index + 1
            else:
                nodelist_length = nodelist_length + intersections[index]
                index = index + 1
    return nodelist_length,layerlist_length
'''                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
            
    
    