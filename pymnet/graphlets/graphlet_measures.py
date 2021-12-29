"""Module for graphlet data analysis
"""
import pymnet
import math
from scipy.stats import spearmanr
from collections import defaultdict as dd

def orbit_counts_all(net, n, nets, invs, auts, orbit_list, allowed_aspects='all'):
    '''
    Computes the orbit counts for all the nodes in net
    
    Parameters
    ----------
    net : network
    n : int
        max number of nodes
    nets : dict (key: n_nodes, value: list of networks)
        Graphlets, as produced by graphlets
    invs : dict (key: str(complete invariant), value: tuple(n_nodes, net_index in nets))
        complete invariants of the graphlets, as produced by graphlet
    auts : dd (key: (n_nodes, net_index, node), value: node)
        automorphisms, as produced by automorphism_orbits
    orbit_list : list of orbits
        as returned by ordered_orbit_list
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
        
    Returns
    -------
    orbits : dd (key: (node, orbit), value: count)
        Orbit counts for all the nodes
    
    Notes
    -----
    Should be faster than orbit_counts if the counts are computed for all 
    (/ most of) the nodes
    '''
    
    nodes = net.slices[0]
    layers = net.slices[1]
    
    orbits = dd()
    
    for node in nodes:
        for orbit in orbit_list:
            orbits[node, orbit] = 0
    
    processed = set()
    
    for node0 in nodes:
        node_sets = set()
        set_p = set([frozenset([node0])])
        for _ in range(n - 1):
            set_c = set()
            for p in set_p:
                for node_p in p:
                    for layer in layers:
                        node_o = net.__getitem__((node_p, layer))
                        for neighbor in node_o.iter_total():
                            if not (neighbor[0] in p or neighbor[0] in processed):
                                set_n = frozenset(p | set([neighbor[0]]))
                                set_c.add(set_n)
                                
            node_sets = node_sets.union(set_c)
            set_p = set_c.copy()
            
        processed.add(node0)
        for node_comb in node_sets:
            sub_net = pymnet.subnet(net, node_comb, layers)
            ci_sub = str(pymnet.get_complete_invariant(sub_net, allowed_aspects=allowed_aspects))
            if ci_sub not in invs:
                raise KeyError('The network contains a graphlet not found in the pre-constructed complete invariant dictionary (invs). This can be caused by invs creation not being compatible with the attributes of the network. For example, the network might not be fully interconnected.')
            i = invs[ci_sub][0]
            j = invs[ci_sub][1]
            nw = nets[i][j]
            iso = pymnet.get_isomorphism(sub_net, nw, allowed_aspects=allowed_aspects)
            for node in node_comb:
                if node in iso[0]:
                    orbits[node, (i, j, auts[i, j, iso[0][node]])] += 1
                else:
                    orbits[node, (i, j, auts[i, j, node])] += 1
                    
        for layer in layers:
            nls = list(net[node0,:,layer])
            for node1 in nls:
                net[node0, node1[0], layer] = 0 #remove edges
    
    return orbits

def orbit_numbers(n, nets, auts):
    '''
    Gives numbers to the orbits
    
    Parameters
    ----------
    n : int
        Max number of nodes in the graphlets
    nets : dict (key: n_nodes, value: list of networks)
        Graphlets, as given by graphlets
    auts : dd (key: (n_nodes, net_index, node), value: node)
        Automorphism orbits, as given by automorphism_orbits
        
    Returns
    -------
    orbit_is : dict
        Orbit numbers, keys are orbits in form (n_nodes, net_index, node)
    '''
    
    orbit_is = {}
    for k in range(2, n+1):
        for j in range(len(nets[k])):
            net = nets[k][j]
            for node in net.slices[0]:
                aut = auts[(k,j,node)]
                if not (k,j,aut) in orbit_is:
                    orbit_is[(k,j,aut)] = len(orbit_is)
            
    return orbit_is
    
    

def ordered_orbit_list(orbit_is):
    '''
    Returns list of orbits ordered based on the orbit numbers
    
    Parameters
    ----------
    orbit_is : dict
        Orbit numbers, keys are orbits in form (n_nodes, net_index, node)
        
    Returns
    -------
    orbit_list : list of orbits
    '''
    
    orbit_list = [None] * len(orbit_is)
    for orbit in orbit_is:
        i = orbit_is[orbit]
        orbit_list[i] = orbit
        
    return orbit_list
    

    
    
def orbit_counts(n, node0, net, nets, orbits, auts, invs, orbit_list, allowed_aspects='all'):
    '''
    Computes the orbit counts for node0 in net
    
    Parameters
    ----------
    node0 : node
    net : network
    nets : dict (key: n_nodes, value: list of networks)
        graphlets
    orbits : dd (key: (node, orbit), value: count)
        dictionary where the counts will be stored
    auts : dd (key: (n_nodes, net_index, node), value: node)
        automorphism orbits
    invs : dict (key: str(complete invariant), value: tuple(n_nodes, net_index in nets))
        complete invariants of the graphlets
    orbit_list : list of orbits
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
    '''
    
    for orbit in orbit_list:
        orbits[node0, orbit] = 0
    
    layers = net.slices[1]
    node_sets = touching_orbit_nodes(node0, net, n)
    for nodes_s in node_sets:
        sub_net = pymnet.subnet(net, nodes_s, layers)
        ci_sub = str(pymnet.get_complete_invariant(sub_net, allowed_aspects=allowed_aspects))
        i = invs[ci_sub][1]
        n_nodes = invs[ci_sub][0]
        nw = nets[n_nodes][i]
        iso = pymnet.get_isomorphism(sub_net, nw, allowed_aspects=allowed_aspects)
        if node0 in iso[0]:
            orbits[node0, (n_nodes, i, auts[n_nodes, i, iso[0][node0]])] += 1
        else:
            orbits[node0, (n_nodes, i, auts[n_nodes, i, node0])] += 1
            
            
def touching_orbit_nodes(node0, net, max_size):
    
    layers = net.slices[1]
    set_p = set([frozenset([node0])])
    set_c =set()
    node_sets = set()
    
    for _ in range(max_size-1):
        for p in set_p:
            for node in p:
                for layer in layers:
                    node_o = net.__getitem__((node, layer))
                    for neighbor in node_o.iter_total():
                        if not neighbor[0] in p:
                            set_n = frozenset(p | set([neighbor[0]]))
                            set_c.add(set_n)
                            
        node_sets = node_sets.union(set_c)
        set_p = set_c.copy()
        
    return node_sets
    
    
def GCM(orbits):
    '''
    Returns the graphlet correlation matrix
    
    Parameters
    ----------
    orbits : pandas dataframe
        Orbit counts for nodes in the network
    '''
    # add dummy vector
    n_rows = orbits.shape[0]
    n_cols = orbits.shape[1]
    orbits.loc[n_rows] = [1] * n_cols
    
    corr, p = spearmanr(orbits, axis=0)
    
    return corr
    
    
def GCD(gcm1, gcm2):
    '''
    Graphlet correlation distance between two networks
    
    Parameters
    ----------
    gcm1, gcm2 : 2-d array
        Graphlet correlation matrices
        
    Returns
    -------
    gcd : float
        Graphlet correlation distance
    '''
    
    assert gcm1.shape == gcm2.shape, 'matrix dimensions do not match'
    
    gcd = 0
    for i in range(len(gcm1)):
        for j in range(i+1, len(gcm1[i])):
            gcd += (gcm1[i][j] - gcm2[i][j])**2
            
    gcd = math.sqrt(gcd)
    
    return gcd
    
    
def GCD_matrix(gcms):
    '''
    Produce a distance matrix of GCDs between networks
    
    Parameters
    ----------
    gcms : list of 2-d arrays
        Graphlet correlation matrices
        
    Returns
    -------
    gcds : list of lists
        Graphlet correlation distances
    '''
    
    gcds = []
    for gcm1 in gcms:
        gcds_t = []
        for gcm2 in gcms:
            gcd = GCD(gcm1, gcm2)
            gcds_t.append(gcd)
            
        gcds.append(gcds_t)
        
    return gcds
