""" Module for theoretical analysis of graphlets.
"""
import pymnet
import itertools
from collections import defaultdict as dd

def graphlets(n, layers, n_l=None, couplings=None, allowed_aspects="all"):
    '''
    Generate graphlets up to n nodes
    
    Parameters
    ----------
    n : int
        maximum number of nodes
    layers : list of layers
    n_l : int
        Number of layers in the generated graphlets, can be smaller than or equal
        to the number of elements in layers
    couplings : list, str, tuple, None, MultilayerNetwork
        Parameter determining how the layers are coupled, i.e. what 
        inter-layer edges are present.
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
    
    Returns
    -------
    nets : dict (key: n_nodes, value: list of MultiplexNetwork objects)
        graphlets
    invariants : dict (key: str(complete invariant), value: tuple(index in 'nets': n_nodes, index in the list of multiplex networks))
        complete invariants of the graphlets, the values can be used to match the graphlets in 'nets'
    '''
    if n_l==None:
        n_l=len(layers)
    
    nets = {}
    invariants = {}
    nets2 = []
    
    for net_layers in itertools.combinations(layers, n_l):
        layer_combs = layer_combinations(net_layers)
        for layer_comb in layer_combs:
            net = pymnet.MultiplexNetwork(couplings=couplings,fullyInterconnected=True)
            for layer in layer_comb:
                net[0,1,layer]=1
                
            for layer in net_layers:
                net.add_layer(layer)
            
            ci = pymnet.get_complete_invariant(net, allowed_aspects=allowed_aspects)
            ci_s = str(ci)
            if not ci_s in invariants:
                invariants[ci_s] = (2, len(nets2))
                nets2.append(net)
            
    nets[2] = nets2
    
    for i in range(2, n):
        nets_i = nets[i]
        nets_i_1 = []
        for net in nets_i:
            net_nodes = net.slices[0]
            net_layers = list(net.slices[1])
            net_layers.sort()
            layer_combs = layer_combinations(net_layers)
            for n_n in range(1, i+1):
                for node_comb in itertools.combinations(range(i), n_n):
                    node_layers = [layer_combs] * n_n
                    for node_layer_comb in itertools.product(*node_layers):
                        new_net = pymnet.subnet(net, net_nodes, net_layers)
                        for node_i in range(n_n):
                            node = node_comb[node_i]
                            for layer in node_layer_comb[node_i]:
                                new_net[node, i, layer] = 1
                        
                        for layer in net_layers:
                            new_net.add_layer(layer)
                        # check if isomorphic with a previous graph & add only if not isomorphic
                        ci = pymnet.get_complete_invariant(new_net, allowed_aspects=allowed_aspects)
                        ci_s = str(ci)
                        if not ci_s in invariants:
                            invariants[ci_s] = (i+1, len(nets_i_1))
                            nets_i_1.append(new_net)
                            
        nets[i+1] = nets_i_1
        
    return nets, invariants
    
    
def automorphism_orbits(nets, allowed_aspects='all'):
    '''
    Computes the node automorphism orbits of each network in nets
    
    Paramaters
    ----------
    nets : dict (key: n_nodes, value: list of networks (MultiplexNetwork) )
        Graphlets, see function 'graphlets'
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
    
    Returns
    -------
    auts : dict (key: (n_nodes, net_index, node), value: node_orbit_index)
        Automorphism orbits. 'n_nodes' is the key in 'nets'. 'net_index' is the
        index in the list of networks. 'node' is the node name in the given network.
        'node_orbit_index' gets the same value for nodes that are in the same orbit.
    '''
    
    auts = dd()
    for n_nodes in nets:
        for i in range(len(nets[n_nodes])):
            net = nets[n_nodes][i]
            aut = pymnet.get_automorphism_generators(net, allowed_aspects=allowed_aspects)
            for node in net.slices[0]:
                auts[n_nodes, i, node] = set([node])
            for a in aut:
                for key in a[0]:
                    for j in net.slices[0]:
                        if key in auts[n_nodes, i, j]:
                            auts[n_nodes, i, j] = auts[n_nodes, i, j].union(auts[n_nodes, i, a[0][key]])
                    
            for node in net.slices[0]:
                auts[n_nodes, i, node] = min(auts[n_nodes, i, node])
                
    return auts
    
def automorphism_orbits_nl(nets, allowed_aspects='all'):
    '''
    computes the automorphism orbits for node-layers for each network in nets
    
    Parameters
    ----------
    nets: dict (key: n_nodes, value: list of networks)
        graphlets
    
    Returns
    -------
    auts: dd (key: (n_nodes, net_index, (node, layer)), value: (node, layer))
    '''
    
    auts = dd()
    for n_nodes in nets:
        for i in range(len(nets[n_nodes])):
            net = nets[n_nodes][i]
            aut = pymnet.get_automorphism_generators(net, allowed_aspects=allowed_aspects, include_fixed=True)
            for nl in net.iter_node_layers():
                auts[n_nodes, i, nl] = set([nl])
                
            for a in aut:
                for key_n in a[0]:
                    for key_l in a[1]:
                        for nl in net.iter_node_layers():
                            if (key_n, key_l) in auts[n_nodes, i, nl]:
                                nl_2 = (a[0][key_n], a[1][key_l])
                                auts[n_nodes, i , nl] = auts[n_nodes, i, nl].union(auts[n_nodes, i, nl_2])
                                
            for nl in net.iter_node_layers():
                auts[n_nodes, i, nl] = min(auts[n_nodes, i, nl])
                
    return auts
    

    
def orbit_equations(n, nets, auts, invs, allowed_aspects='all'):
    '''
    Generate orbit equations for up to n nodes

    The equations are in following formatting:
    
    orbits : this represents node orbits of graphlets
    
    Parameters
    ----------
    n : int
        maximum number of nodes
    nets : dict (key: n_nodes, value: list of nets)
        graphlets, as returned by graphlets
    auts : dd (key: (n_nodes, net_index, node), value: node)
        automorphisms, as returned by automorphism_orbits
    invs : dict (key: str(complete invariant), value: tuple(n_nodes, net_index in nets))
        complete invariants of the graphlets, as returned by graphlets
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
    
    Returns
    -------
    orbit_eqs : dict (key: orbits, value: dict (key: orbit, value: coefficient))
        
    '''
    
    orbit_eqs = dd()
    
    orbit_lists = list_orbits(auts)
    
    for n_nodes1 in range(2,min(n+1,4)):    
        for orbit in orbit_lists[n_nodes1]:
            node1 = orbit[2]
            for n_nodes in orbit_lists:
                comb_n_nodes = n_nodes1 + n_nodes - 1
                if comb_n_nodes <= n:
                    for orbit2 in orbit_lists[n_nodes]:
                        if ((orbit, 1), (orbit2, 1)) in orbit_eqs:
                            continue
                        
                        new_nets = {}
                        new_orbits = set()
                        comb_nets = combine_orbits(orbit, orbit2, nets, allowed_aspects=allowed_aspects)
                        if comb_nets == None:
                            continue
                        
                        for k in range(len(comb_nets)):
                            comb_nets[k] = (comb_nets[k], [node1])
                        merge_nets = {}
                        min_nodes = max([n_nodes1, n_nodes]) + 1
                        merge_nets[comb_n_nodes] = comb_nets
                        for m in range(comb_n_nodes, min_nodes, -1): #TODO: make this merge thingy smarter, use combinations
                            merge_nets[m-1] = []
                            for m_net in merge_nets[m]:
                                merge_nets[m-1] += merge_nodes(m_net[1], m_net[0], allowed_aspects=allowed_aspects)
                                
                            comb_nets += merge_nets[m-1]
                            
                        add_e_nets = []
                        for k in range(len(comb_nets)):
                            c_net = comb_nets[k][0]
                            both_orbit_nodes = comb_nets[k][1]
                            nets_e = add_possible_edges(both_orbit_nodes, c_net)
                            for net_e in nets_e:
                                add_e_nets.append((net_e, both_orbit_nodes))
                            
                            
                        comb_nets += add_e_nets
                        for comb_net in comb_nets:
                            ci_comb = str(pymnet.get_complete_invariant(comb_net[0], allowed_aspects=allowed_aspects))
                            iso_net = invs[ci_comb]
                            iso = pymnet.get_isomorphism(comb_net[0], nets[iso_net[0]][iso_net[1]], allowed_aspects=allowed_aspects)
                            if node1 in iso[0]:
                                node_o = iso[0][node1]
                            else:
                                node_o = node1
                                
                            new_orbit = (iso_net[0], iso_net[1], auts[iso_net[0], iso_net[1], node_o])
                            if not new_orbit in new_orbits:
                                new_orbits.add(new_orbit)
                                new_nets[new_orbit] = comb_net
                        
                        if orbit == orbit2:
                            times = 2
                            key = ((orbit, times))
                        else:
                            times = 1
                            key = ((orbit2, 1), (orbit, 1))
                            
                        orbit_eqs[key] = {}
                        for i in new_orbits:
                            coef = coefficient(node1, new_nets[i][1], orbit, orbit2, new_nets[i][0], nets, auts, invs, allowed_aspects=allowed_aspects)
                            if coef > 0:
                                orbit_eqs[key][i] = coef
                                
    return orbit_eqs
    
    
def subtrahend(orbit1, orbit2, nets, auts, invs, allowed_aspects='all'):
    '''
    Returns the subtrahend for orbit2 in orbit equations (the value that is
    subtracted in the upper part of the binomial coefficient on the sleft sides
    of the orbit equation)
    
    Parameters
    ----------
    orbit1, orbit2 : tuple (n_nodes, net_index, node_orbit_index)
        These can extract from the output of orbit_equations, n_nodex, net_index,
        and node_orbit_index should match those of parameter auts
    nets : dict (key: n_nodes, value: list of networks)
        graphlets, as produced by graphlets
    auts : dd (key: (n_nodes, net_index, node), value: node_orbit_index)
        as produced by automorphism_orbits
    
    Returns
    -------
    sub_max : int
    
    Notes
    -----
    assumes orbit2 has at most the same number of nodes as orbit1
    '''
    
    sub_max = 0
    n_nodes1 = orbit1[0]
    n_nodes2 = orbit2[0]
    net1 = nets[n_nodes1][orbit1[1]]
    net2 = nets[n_nodes2][orbit2[1]]
    the_node = orbit1[2]
    layers = net1.slices[1]
    nodes = net1.slices[0] - set([the_node])
    for partition in partitions_with_remainder(nodes, n_nodes2-1):
        sub = 0
        for nodes_s in partition:
            nodes_g = set(nodes_s) | set([the_node])
            sub_net = pymnet.subnet(net1, nodes_g, layers)
            ci_sub = str(pymnet.get_complete_invariant(sub_net, allowed_aspects=allowed_aspects))
            if ci_sub in invs and invs[ci_sub] == (n_nodes2, orbit2[1]):
                iso = pymnet.get_isomorphism(sub_net, net2, allowed_aspects=allowed_aspects)
                if the_node in iso[0]:
                    iso_node = iso[0][the_node]
                else:
                    iso_node = the_node
                    
                if auts[n_nodes2, orbit2[1], iso_node] == orbit2[2]:
                    sub += 1
                    
        sub_max = max(sub_max, sub)
        
    return sub_max
    
    
def list_orbits(auts):
    '''
    Lists all orbits
    
    Parameters
    ----------
    auts: dd (key: (n_nodes, net_index, node), value: node)
        Automorphism orbits
    
    Returns
    -------
    orbit_lists: dict (key: n_nodes, value: list of orbits)
    '''
    
    orbit_lists = {}
    for key in auts:
        n_nodes = key[0]
        net_i = key[1]
        orbit = auts[key]
        if not n_nodes in orbit_lists:
            orbit_lists[n_nodes] = []
        if not (n_nodes, net_i, orbit) in orbit_lists[n_nodes]:
            orbit_lists[n_nodes].append((n_nodes, net_i, orbit))
            
    return orbit_lists
    
    
def combine_orbits(orbit1, orbit2, nets, allowed_aspects='all'):
    '''
    Combines orbits orbit1 and orbit2
    
    Parameters
    ----------
    orbit1, orbit2: tuple (n_nodes, net_index, node)
    nets: dict (key: n_nodes, value: list of networks)
        graphlets
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
        
    Returns
    -------
    new_nets: list of networks, None
        networks obtained by combining the orbits (no links added, no merging of nodes),
        returns None if orbits cannot be combined (graphlets have different layers)
        
    Notes
    -----
    atm works only with node-layer isomorphisms, now also vertex isomorphisms
    node1 will be the_node
    '''
    
    net1 = nets[orbit1[0]][orbit1[1]]
    net2 = nets[orbit2[0]][orbit2[1]]
    node1 = orbit1[2]
    node2 = orbit2[2]
    
    nodeNames = {}
    layerNames = {}
    
    nodeNames[node2] = node1
    nodes2 = net2.slices[0]
    n_nodes2 = len(nodes2)
    nodes1 = net1.slices[0]
    layers1 = net1.slices[1]
    layers2 = net2.slices[1]
    if layers1 != layers2:
        return None
    
    for (nodeName, newName) in zip(nodes2 - set([node2]), range(-2, -n_nodes2 - 1, -1)): # could be changed to range(-1,-n_nodes2,-1)?
        nodeNames[nodeName] = newName
    
    new_nets = []
    new_invs = set()
    new_net = pymnet.subnet(net1, nodes1, layers1)    
    net2_r = pymnet.transforms.relabel(net2, nodeNames, layerNames)
    for e in net2_r.edges:
        if e[0] != e[1]:
            new_net[e[0], e[1], e[2], e[3]] = e[4]
        
    new_nets.append(new_net)
    ci = str(pymnet.get_complete_invariant(new_net, allowed_aspects=allowed_aspects))
    new_invs.add(ci)
    
    if allowed_aspects != [0]:
        for perm in itertools.permutations(layers2, len(layers2)):
            for i in range(len(perm)):
                layerNames[perm[i-1]] = perm[i]
                
            new_net = pymnet.subnet(net1, nodes1, layers1)
            net2_r = pymnet.transforms.relabel(net2, nodeNames, layerNames)
            for e in net2_r.edges:
                if e[0] != e[1]:
                    new_net[e[0], e[1], e[2], e[3]] = e[4]
            
            ci = str(pymnet.get_complete_invariant(new_net, allowed_aspects=allowed_aspects))
            if not ci in new_invs:
                new_nets.append(new_net)
                new_invs.add(ci)
            
    return new_nets
    
    
def merge_nodes(both_orbit_nodes, net, allowed_aspects='all'):
    '''
    Merges nodes from different orbits,
    each returned network has different combination of nodes merged, 
    merges only one pair of nodes
    
    Parameters
    ----------
    both_orbit_nodes : list of nodes
    net : network
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
    
    Returns
    -------
    new_nets_and_nodes : list of tuples (net, both_orbit_nodes)
    
    Notes
    -----
    assumes negative nodes belong to the same orbit
    works for both multiplex and multilayer networks (1 aspect)
    '''
    
    nodes_a = net.slices[0]
    nodes = nodes_a - set(both_orbit_nodes)
    nodes1 = []
    nodes2 = []
    for node in nodes:
        if node < 0:
            nodes2.append(node)
        else:
            nodes1.append(node)
            
    layers = net.slices[1]
    new_nets_and_nodes = []
    new_nets = []
    new_invs = set()
    
    for comb in itertools.product(nodes1, nodes2):
        node1 = comb[0]
        node2 = comb[1]
        l1 = set()
        l2 = set()
        for nl in net.iter_node_layers():
            if nl[0] == node1:
                l1.add(nl[1])
            elif nl[0] == node2:
                l2.add(nl[1])
                
        if not (l1 <= l2 and l1 >= l2): #nodes not present in the same layers
            continue
        
        nodes_s1 = both_orbit_nodes + [node1]
        nodes_s2 = both_orbit_nodes + [node2]
        sub1 = pymnet.subnet(net, nodes_s1, layers)
        sub2 = pymnet.subnet(net, nodes_s2, layers)
        if not pymnet.is_isomorphic(sub1, sub2, allowed_aspects=[0]): #not same links to the_node
            continue
        
        nodes_s = nodes_a - set([node2])
        new_net = pymnet.subnet(net, nodes_s, layers)
        for layer in layers: 
            node2_o = net.__getitem__((node2, layer))
            for neighbor in node2_o.iter_total():
                if neighbor[0] != node2:
                    new_net[node1, neighbor[0], layer, neighbor[1]] = 1
        
        ci = str(pymnet.get_complete_invariant(new_net, allowed_aspects=allowed_aspects))
        if not ci in new_invs:
            new_nets.append(new_net)
            new_nets_and_nodes.append((new_net, both_orbit_nodes + [node1]))
            new_invs.add(ci)
            
    return new_nets_and_nodes
 

def add_possible_edges(both_orbit_nodes, net):
    '''
    Adds all possible edge combinations between nodes from different orbits
    
    Parameters
    ----------
    both_orbit_nodes : list of nodes
        nodes that belong to both orbits
    net : network
    
    Returns
    -------
    nets : list of networks
    
    Notes
    -----
    assumes negative nodes belong to the same orbit
    returned networks can be isomorphic
    '''
    
    nodes = net.slices[0] - set(both_orbit_nodes)
    nodes1 = []
    nodes2 = []
    for node in nodes:
        if node < 0:
            nodes2.append(node)
        else:
            nodes1.append(node)
            
    edges = list(itertools.product(nodes1, nodes2))
    n_edges = len(edges)
    
    net_nodes = net.slices[0]
    net_layers = net.slices[1]
    layer_combs = layer_combinations(net_layers)
    
    nets = []
    
    for n_e in range(1, n_edges+1):
        for edge_comb in itertools.combinations(edges, n_e):
            edge_layers = [layer_combs] * n_e
            for edge_layer_comb in itertools.product(*edge_layers):
                new_net = pymnet.subnet(net, net_nodes, net_layers)
                for edge_i in range(n_e):
                    edge = edge_comb[edge_i]
                    for layer in edge_layer_comb[edge_i]:
                        new_net[edge[0], edge[1], layer] = 1
                
                nets.append(new_net)
                    
    return nets
    
    
def layer_combinations(layers):
    
    n_layers = len(layers)
    layer_combs = []
    for n_l in range(1, n_layers + 1):
        for layer_comb in itertools.combinations(layers, n_l):
            layer_combs.append(layer_comb)
        
    return layer_combs
    
    
def coefficient(the_node, both_orbit_nodes, orbit1, orbit2, net, nets, auts, invs, allowed_aspects='all'):
    '''
    Returns the coefficient for the orbit (defined by the_node and net) for the orbit count equations
    
    Parameters
    ----------
    the_node : node (index)
        the node that touches both orbits: orbit1 and orbit2
    both_orbit_nodes : list of nodes
        nodes that belonged to both orbits
    orbit1, orbit2 : tuple (n_nodes, net_index, node)
        orbits that were used to form net
    net : network
        network that was formed from orbit1 and orbit2 (also by adding links and merging nodes)
    nets : dict (key: n_nodes, value: list of networks)
        graphlets
    auts : dd (key: (n_nodes, net_index, node), value: node)
        automorphism orbits
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
    '''
    
    nodes_a = net.slices[0]
    nodes = nodes_a - set([the_node])
    
    n_both = len(both_orbit_nodes)
    
    coef = 0
    
    if n_both > 1:
        for shared_nodes in itertools.combinations(nodes, n_both-1):
            both_nodes = set(shared_nodes) | set([the_node])
            nodes_s = nodes - set(shared_nodes)
            coef += coefficient_help(nodes_s, the_node, both_nodes, orbit1, orbit2, net, nets, auts, invs, allowed_aspects)
                
    else:
        coef += coefficient_help(nodes, the_node, both_orbit_nodes, orbit1, orbit2, net, nets, auts, invs, allowed_aspects)
    
    if orbit1 == orbit2:
        times = 2
    else:
        times = 1
    coef = coef / times
                
    return coef
    

def coefficient_help(nodes, the_node, both_orbit_nodes, orbit1, orbit2, net, nets, auts, invs, allowed_aspects='all'):
    '''
    helper function for coefficient
    '''
    
    coef = 0
    
    nodes_a = net.slices[0]
    layers = net.slices[1]
    
    net1 = nets[orbit1[0]][orbit1[1]]
    net2 = nets[orbit2[0]][orbit2[1]]
    n_nodes1 = len(net1.slices[0])
    
    for node_comb in itertools.combinations(nodes, n_nodes1-len(both_orbit_nodes)):
        nodes_s2 = nodes_a - set(node_comb)        
        nodes_s1 = (nodes_a - nodes_s2) | set(both_orbit_nodes)
        sub1 = pymnet.subnet(net, nodes_s1, layers)
        sub2 = pymnet.subnet(net, nodes_s2, layers)
        ci_sub1 = str(pymnet.get_complete_invariant(sub1, allowed_aspects=allowed_aspects))
        ci_sub2 = str(pymnet.get_complete_invariant(sub2, allowed_aspects=allowed_aspects))
        if not ci_sub1 in invs or not ci_sub2 in invs:
            continue
        if invs[ci_sub1] == (orbit1[0], orbit1[1]) and invs[ci_sub2] == (orbit2[0], orbit2[1]):
            iso1 = pymnet.get_isomorphism(sub1, net1, allowed_aspects=allowed_aspects)
            iso2 = pymnet.get_isomorphism(sub2, net2, allowed_aspects=allowed_aspects)
            if the_node in iso1[0]:
                iso_node1 = iso1[0][the_node]
            else:
                iso_node1 = the_node
                
            if the_node in iso2[0]:
                iso_node2 = iso2[0][the_node]
            else:
                iso_node2 = the_node
                
            if auts[orbit1[0], orbit1[1], iso_node1] == orbit1[2] and auts[orbit2[0], orbit2[1], iso_node2] == orbit2[2]:
                coef += 1
                
    return coef
    
    
def orbit_name(node, net, nets, invs, auts, allowed_aspects='all'):
    '''
    finds the name of the orbit given node and net
    '''
    
    ci = str(pymnet.get_complete_invariant(net, allowed_aspects=allowed_aspects))
    i, j = invs[ci]
    net_i = nets[i][j]
    iso = pymnet.get_isomorphism(net, net_i, allowed_aspects=allowed_aspects, include_fixed=True)
    k = auts[i, j, iso[0][node]]
    
    return (i, j, k)
    
    
def partitions(s, r): #Gareth Rees https://stackoverflow.com/questions/14559946/producing-all-groups-of-fixed-length-combinations
    """
    Generate partitions of the iterable `s` into subsets of size `r`.

    >>> list(partitions(set(range(4)), 2))
    [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
    """
    s = set(s)
    assert(len(s) % r == 0)
    if len(s) == 0:
        yield ()
        return
    first = next(iter(s))
    rest = s.difference((first,))
    for c in itertools.combinations(rest, r - 1):
        first_subset = (first,) + c
        for p in partitions(rest.difference(c), r):
            yield (first_subset,) + p

def partitions_with_remainder(s, r): #Gareth Rees https://stackoverflow.com/questions/14559946/producing-all-groups-of-fixed-length-combinations
    """
    Generate partitions of the iterable `s` into subsets of size
    `r` plus a remainder.

    >>> list(partitions_with_remainder(range(4), 2))
    [((0, 1, 2, 3),), ((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
    >>> list(partitions_with_remainder(range(3), 2))
    [((0, 1, 2),), ((1, 2), (0,)), ((0, 2), (1,)), ((0, 1), (2,))]
    """
    s = set(s)
    for n in xrange(len(s), -1, -r): # n is size of remainder.
        if n == 0:
            for p in partitions(s, r):
                yield p
        elif n != r:
            for remainder in itertools.combinations(s, n):
                for p in partitions(s.difference(remainder), r):
                    yield p + (remainder,)
