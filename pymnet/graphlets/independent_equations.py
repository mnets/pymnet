"""Module containing heuristics for finding independent equations of multiplex graphlets.
"""

from . import graphlets
import itertools
from collections import defaultdict as dd

def independent_equations(n, n_l, layers, allowed_aspects='all'):
    '''
    Computes a set of independent equations
    
    Parameters
    ----------
    n : int
        Max number of nodes
    n_l : int
        Number of layers in the generated graphlets, can be smaller than or equal
        to the number of elements in layers
    layers : list
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
        
    Returns
    -------
    inds : set
        Independent equations, keys for eqs
    eqs : dd (key: orbits, value: dict (key: orbit, value: coefficient))
        Equations
    
    Notes
    -----
    Implemented for up to 4-node graphlets
    '''    
    
    nets, invs = graphlets.graphlets(n, layers, n_l, allowed_aspects=allowed_aspects)
    auts = graphlets.automorphism_orbits(nets, allowed_aspects=allowed_aspects)
    orbit_lists = graphlets.list_orbits(auts)
    eqs = graphlets.orbit_equations(n, nets, auts, invs, allowed_aspects=allowed_aspects)
    inds = set()
    for layer_comb in itertools.combinations(layers, n_l):
        if len(layers) == n_l:
            eqs_sub = eqs
        else:
            eqs_sub = eqs_in_layers(layer_comb, eqs, nets)
        
        independent, undefined, set_eqs = definitely_independent(eqs_sub)
        
        if n == 3:
            inds = inds | independent
            continue
        
        eqNet = eq_network(undefined, set_eqs, n, nets, auts, invs, allowed_aspects=allowed_aspects)
        
        for eq in eqs_sub:
            for i in range(2, 4):
                for orbit in orbit_lists[i]:
                    if too_many_nodes(eq, orbit, n):
                        break
                    
                    if not orbit_in_layers(orbit, layer_comb, nets):
                        continue
                    
                    _ = three_orbit_equations(eq, orbit, set_eqs, eqNet, nets, auts, invs, allowed_aspects=allowed_aspects)
                    
        for dep in eqNet.items():
            if len(dep[1]) == 0:
                independent.add(dep[0])
                undefined.remove(dep[0])
                
        for ind in independent:
            eqNet[ind] = []
            
        independent, deps, eqNet = all_inds_and_deps(eqNet)
        inds = inds | independent
    
    return inds, eqs
    
    
def redundant_orbits(inds, eqs, orbit_is, orbit_list):
    '''
    Picks a set of redundant orbits
    
    Parameters
    ----------
    inds : set
        Independent equations, keys for eqs
    eqs : dd (key: orbits, value: dict (key: orbit, value: coefficient))
        Equations
    orbit_is : dict
        Orbit numbers, keys are orbits in form (n_nodes, net_index, node)
    orbit_list : list of orbits
    
    Returns
    -------
    reds : list of strs
        Redundant orbits
    '''
    
    redundants = set()
    for eq in inds:
        os = set()
        for orbit in eqs[eq]:
            o = orbit_is[orbit]
            os.add(o)
            
        o_max = max(os)
        while o_max in redundants:
            os = os - set([o_max])
            o_max = max(os)
            
        redundants.add(o_max)
        
    redundants = list(redundants)
    reds = []
    for i in redundants:
        orbit = orbit_list[i]
        reds.append(str(orbit))
        
    return reds
    
    
def eqs_in_layers(layers, eqs, nets):
    '''
    Finds the subset of equations that use only given layers.
    
    Parameters
    ----------
    layers : iterable
    eqs : dd (key: orbits, value: dict (key: orbit, value: coefficient))
        Equations
    nets : dict (key: n_nodes, value: list of networks)
        Graphlets
        
    Returns
    -------
    eqs_sub : dd (key: orbits, value: dict (key: orbit, value: coefficient))
    '''
    
    eqs_sub = dd()
    
    layers = set(layers)
    nets_sub = set()
    for n in nets:
        for i in range(len(nets[n])):
            if nets[n][i].slices[1] == layers:
                nets_sub.add((n, i))
                
    for eq in eqs:
        if len(eq[0]) != 3:
            n = eq[0][0][0]
            i = eq[0][0][1]
            
        else:
            n = eq[0][0]
            i = eq[0][1]
            
        if (n, i) in nets_sub:
            eqs_sub[eq] = eqs[eq]
        
    return eqs_sub
    
    
def orbit_in_layers(orbit, layers, nets):
    '''
    Returns True if orbit resides in graphlet with the given layers.
    
    Parameters
    ----------
    orbit : tuple
        (n_nodes, net_i, node)
    layers : iterable
    nets : dict (key: n_nodes, value: list of networks)
        Graphlets
    '''
    
    n = orbit[0]
    i = orbit[1]
    
    if nets[n][i].slices[1] == set(layers):
        return True
        
    else:
        return False

    
def definitely_independent(eqs):
    '''
    Returns all the equations up to 3 nodes & equations that contain variables
    that do not exist in any other equations.
    
    Parameters
    ----------
    eqs : dd (key: orbits, value: dict (key: orbit, value: coefficient))
        Equations
        
    Returns
    -------
    independent : set
        Definitely independent equations
    undefined : set
        Equations whose independency is still undefined
    set_eqs : dict (key: eq, value: set of orbits)
        Equations in set form disregarding coefficients
    '''
    
    independent = set()
    undefined = set()
    set_eqs = {}
    
    eq_sets = []
    eq_keys = []
    for eq in eqs:
        eq_set = set()
        for orbit in eqs[eq]:
            eq_set.add(orbit)
            
        set_eqs[eq] = eq_set.copy()
        if len(eq[0]) != 3:
            i1 = eq[0][0]
            i2 = eq[1][0]
            if i1[0] == 2 and i2[0] == 2:
                independent.add(eq)
            
            eq_set.add(i1)
            eq_set.add(i2)
            
        else:
            i = eq[0]
            if i[0] == 2:
                independent.add(eq)
            
            eq_set.add(i)
            
        eq_sets.append(eq_set)
        eq_keys.append(eq)
        
    for i in range(len(eq_keys)):
        eq = eq_keys[i]
        if eq in independent:
            continue
        
        j = 0
        eq_set = eq_sets[i].copy()
        while len(eq_set) > 0 and j < len(eq_sets):
            if i != j:
                eq_set = eq_set - eq_sets[j]
                
            j += 1
            
        if len(eq_set) > 0:
            independent.add(eq)
        else:
            undefined.add(eq)
            
    return independent, undefined, set_eqs
    
    
def eq_network(undefined, set_eqs, max_nodes, nets, auts, invs, allowed_aspects='all'):
    '''
    Forms dependency networks of equations.
    
    Parameters
    ----------
    undefined : set
        Equations whose independency is to be determined
    set_eqs : dict (key: eq, value: set of orbits)
        Equations in set form disregarding coefficients
    max_nodes : int
    nets : dict (key: n_nodes, value: list of nets)
        graphlets
    auts : dd (key: (n_nodes, net_index, node), value: node)
        automorphisms
    invs : dict (key: str(complete invariant), value: tuple(n_nodes, net_index in nets))
        complete invariants of the graphlets
    allowed_aspects : list, string
        the aspects that can be permutated when computing isomorphisms
        
    Returns
    -------
    depends : dict (key: eq, value: list of eqs)
    
    Notes
    -----
    Doesn't compute all 3-orbit equations
    '''

    depends = {}
    
    for un in undefined:
        orbits = []
        if len(un[0]) != 3:
            orbit1 = un[0][0]
            orbit2 = un[1][0]
            orbits.append(orbit1)
            orbits.append(orbit2)
            
        else:
            orbit = un[0]
            orbits.append(orbit)
        
        deps = []
        for i in range(len(orbits)):
            orbit = orbits[i]
            if len(orbits) == 1:
                multi = orbit
            else:
                multi = orbits[i-1]
            
            for eq in set_eqs:
                if orbit in set_eqs[eq]:
                    dep = set([eq])
                        
                    if too_many_nodes(eq, multi, max_nodes):
                        continue
                    
                    eq3 = three_orbit_equations(eq, multi, set_eqs, depends, nets, auts, invs, allowed_aspects=allowed_aspects)
                    
                    new_eqs = find_equations(multi, eq, set_eqs) - set([un])
                    if len(new_eqs) == 0:
                        continue
                    
                    dep = dep | new_eqs | set([eq3])
                    deps.append(dep) #TODO: remove this line!!! does this still hold??
                    '''
                    for eq3 in eqs3:
                        if un in eq3:
                            print(un)
                        dep1 = dep | eq3
                        deps.append(dep1)
                    '''
                        
        depends[un] = deps
        
    return depends
    
    
def too_many_nodes(eq, orbit, max_nodes):
    
    n = orbit[0]
    
    if len(eq[0]) != 3:
        orbit1 = eq[0][0]
        orbit2 = eq[1][0]
        n1 = orbit1[0]
        n2 = orbit2[0]
        
        if (n1 + n2 + n - 2) > max_nodes:
            return True
            
    else:
        orbit1 = eq[0]
        n1 = orbit1[0]
        
        if (2 * n1 + n - 2) > max_nodes:
            return True
            
    return False


def find_equations(orbit, eq, set_eqs):
    
    eqs = set()
    
    for orbit_eq in set_eqs[eq]:
        key = find_key(orbit, orbit_eq, set_eqs)
        if key != None:
            eqs.add(key)
        else:
            eqs = set()
            break
        
    return eqs


def find_key(orbit1, orbit2, eqs):
    
    if orbit1 == orbit2 and (orbit1, 2) in eqs:
        return (orbit1, 2)
    
    if ((orbit1, 1), (orbit2, 1)) in eqs:
        return ((orbit1, 1), (orbit2, 1))
    
    if ((orbit2, 1), (orbit1, 1)) in eqs:
        return ((orbit2, 1), (orbit1, 1))
    
    return None
    
    
def three_orbit_equations(eq, orbit, set_eqs, eq_net, nets, auts, invs, allowed_aspects='all'):
    
    if len(eq[0]) != 3:
        orbit1 = eq[0][0]
        orbit2 = eq[1][0]
        
    else:
        orbit1 = eq[0]
        orbit2 = orbit1
    
    orbits = (orbit1, orbit2, orbit)
    for key3 in itertools.permutations(orbits):
        if key3 in eq_net:
            return key3
        
    eqs_list = []
    
    if orbit1 == orbit2 and orbit2 == orbit:
        eqs = find_equations(orbit, eq, set_eqs) | set([eq])
        eqs_list.append(eqs)
        
    elif orbit1 == orbit2:
        n1 = orbit1[0]
        n = orbit[0]
        if n1 > n:
            eqs = find_equations(orbit, eq, set_eqs) | set([eq])
            eqs_list.append(eqs)
            
        else:
            sub = graphlets.subtrahend(orbit, orbit1, nets, auts, invs, allowed_aspects=allowed_aspects)
            key = find_key(orbit, orbit1, set_eqs)
            if sub == 0:
                eqs = find_equations(orbit, eq, set_eqs) | set([eq])
                eqs_list.append(eqs)
                
            else:
                eqs = find_equations(orbit, eq, set_eqs) | set([eq, key])
                eqs_list.append(eqs)
                
            eqs = find_equations(orbit1, key, set_eqs) | set([key])
            eqs_list.append(eqs)
            
    elif orbit1 != orbit2 and orbit2 == orbit:
        eqs = find_equations(orbit, eq, set_eqs) | set([eq])
        eqs_list.append(eqs)
        
        sub = graphlets.subtrahend(orbit1, orbit, nets, auts, invs, allowed_aspects=allowed_aspects)
        key = find_key(orbit2, orbit, set_eqs)
        if sub == 0:
            eqs = find_equations(orbit1, key, set_eqs) | set([key])
            eqs_list.append(eqs)
            
        else:
            eqs = find_equations(orbit, eq, set_eqs) | set([eq, key])
            eqs_list.append(eqs)
            
    elif orbit1 != orbit2 and orbit1 == orbit:
        eqs = find_equations(orbit, eq, set_eqs) | set([eq])
        eqs_list.append(eqs)
        
        key = find_key(orbit1, orbit, set_eqs)
        eqs = find_equations(orbit2, key, set_eqs) | set([key])
        eqs_list.append(eqs)
        
    else:
        eqs = find_equations(orbit, eq, set_eqs) | set([eq])
        eqs_list.append(eqs)
        
        key = find_key(orbit1, orbit, set_eqs)
        eqs = find_equations(orbit2, key, set_eqs) | set([key])
        eqs_list.append(eqs)
        
        key = find_key(orbit2, orbit, set_eqs)
        eqs = find_equations(orbit1, key, set_eqs) | set([key])
        eqs_list.append(eqs)
        
    eq_net[key3] = eqs_list
    
    return key3
    
    
def all_inds_and_deps(eq_net):
    
    eqs = []
    eq_is = []
    eq_edges = []
    
    for eq in eq_net:
        n_eqs = len(eq_net[eq])
        if n_eqs > 1:
            eqs.append(eq)
            eq_i = list(range(n_eqs))
            eq_is.append(eq_i)
            eq_edges.append(eq_net[eq])
        elif n_eqs == 1:
            eq_net[eq] = eq_net[eq][0]
            
    max_deps = 0
    inds = set()
    deps = set()
    for edge_comb in itertools.product(*eq_is):
        for i in range(len(edge_comb)):
            eq = eqs[i]
            edges = eq_edges[i][edge_comb[i]]
            eq_net[eq] = edges
            
        SCC = SCCs(eq_net)
        independent, dependent = independents_and_dependents(SCC, eq_net)
        if len(dependent) > max_deps:
            inds = independent
            deps = dependent
            eq_net_best = eq_net.copy()
            max_deps = len(dependent)
            
        #break # remove this!!! only for 4-node 3-layer vertex isomorphism
            
    return inds, deps, eq_net_best
    
    
def SCCs(net):
    
    net_r = reverse(net)
    post = DFS(net_r)
    
    SCC = {}
    k = 1
    visited = set()
    post2 = []
    while len(post) > 0:
        v = post.pop()
        if v not in visited:
            visited2, post2 = explore(v, net, visited, post2)
            SCC[k] = visited2 - visited
            visited = visited2
            k += 1
            
    return SCC
    
    
def reverse(eq_net):
    
    net_r = {}
    
    for eq in eq_net:
        net_r[eq] = set()
        
    for eq1 in eq_net:
        for eq2 in eq_net[eq1]:
            net_r[eq2].add(eq1)
            
    return net_r
    
    
def explore(v, net, visited, post):
    
    visited_c = visited.copy()
    visited_c.add(v)
    if len(net[v]) > 0:
        for u in net[v]:
            if not u in visited_c:
                visited_c, post = explore(u, net, visited_c, post)
            
    post.append(v)
    
    return visited_c, post
    
    
def DFS(net):
    
    visited = set()
    post = []
    for v in net:
        if not v in visited:
            visited, post = explore(v, net, visited, post)
            
    return post
    
    
def independents_and_dependents(SCC, eq_net):
    
    independent = set()
    dependent = set()
    
    for k in SCC:
        three = False
        for eq in SCC[k]:
            if len(eq) == 3:
                dependent.add(eq)
                independent = independent | SCC[k] - set([eq])
                three = True
                break
        
        if not three:
            for eq in SCC[k]:
                both = independent | dependent
                if len(eq_net[eq]) == 0:
                    independent.add(eq)
                elif eq_net[eq] <= both:
                    dependent.add(eq)
                else:
                    independent.add(eq)
                
    return independent, dependent
