"""Package for isomorphisms in multilayer networks.

The package is based on reducing multilayer network isomorphism problems to graph isomorphism problems.
The graph isomorphism problems can be solved using different backends. Currently the following backends
are supported (the functions these backends can be used for are in parenthesis):

- NetworkX :  "nx" (is_isomorphic, get_isomorphism)
- PyBliss : "bliss" (is_isomorphic, get_isomorphism, get_automorphism_generators, get_complete_invariant)
"""

auxbuilder_backends={}
comparison_backends=[]
complete_invariant_backends=[]
automorphism_group_generator_backends=[]
isomorphism_mapping_backends=[]

#lets try to import some backends

try:
    from . import nxbackend
    auxbuilder_backends["nx"]=nxbackend.AuxiliaryGraphBuilderNX
except ImportError:
    pass

try:
    from . import blissbackend
    try:
        blissbackend.bliss.Graph #Bliss import might fail silently...
        auxbuilder_backends["bliss"]=blissbackend.AuxiliaryGraphBuilderBliss
    except AttributeError:
        pass
except ImportError:
    pass



#fill in the backends that are available to do various tasks
for backendname,auxbuilder in auxbuilder_backends.items():
    if auxbuilder.has_comparison:
        comparison_backends.append(backendname)
    if auxbuilder.has_complete_invariant:
        complete_invariant_backends.append(backendname)
    if auxbuilder.has_automorphism_group_generators:
        automorphism_group_generator_backends.append(backendname)
    if auxbuilder.has_isomorphism_mapping:
        isomorphism_mapping_backends.append(backendname)



def is_isomorphic(net1,net2,allowed_aspects="all",backend="auto"):
    """Checks if the two networks are isomorphic.

    Parameters
    ----------
    net1 : MultilayerNetwork
       The first multilayer network.
    net2 : MultilayerNetwork
       The second multilayer network.
    allowed_aspects : list of ints, string
       The aspects that can be permuted in this isomorphism type. Nodes are in aspect 0 by convention.
       Value "all" will allow all permutations, i.e., it gives the (nonpartial) node-layer isomorphism.
    backend : string
       The program to be used for solving the graph isomorphism of the auxiliary graphs. Value "auto" 
       will select the best available candidate. For a list of backends, see documentation of the package.


    Returns
    -------
    is_isomorphic : bool
       True if net1 and net1 are isomorphic, False otherwise.


    References
    ----------
    "Isomorphisms in Multilayer Networks", M. Kivela & M. A. Porter, arXiv:1506.00508 [physics.soc-ph]
    """
    assert len(comparison_backends)>0, "No backends for comparison were imported!"
    if backend=="auto":
        backend=comparison_backends[0]
    else:
        assert backend in comparison_backends, "Backend "+str(backend)+" does not allow comparisons"
        
    auxbuilder=auxbuilder_backends[backend]
    a1=auxbuilder(net1,allowed_aspects)
    a2=auxbuilder(net2,allowed_aspects)
    return a1.compare(a2)

def get_complete_invariant(net,allowed_aspects="all",backend="auto"):
    """Returns a value that is a complete invariant under multilayer network isomorphism.

    Parameters
    ----------
    net : MultilayerNetwork
       The multilayer network.
    allowed_aspects : list of ints, string
       The aspects that can be permuted in this isomorphism type. Nodes are in aspect 0 by convention.
       Value "all" will allow all permutations, i.e., it gives the (nonpartial) node-layer isomorphism.
    backend : string
       The program to be used for solving the graph isomorphism of the auxiliary graphs. Value "auto" 
       will select the best available candidate. For a list of backends, see documentation of the package.


    Returns
    -------
    complete_invariant : object
       The returned object is a complete invariant under the specified multilayer network isomorphism.
       That is, any two objects returned by this function are the same exactly when the two networks are
       isomorphic. Note that the isomorphism types (allowed_aspects) need to match in order for the comparison 
       to be valid. The actual object can depend on the backend that was used.

    References
    ----------
    "Isomorphisms in Multilayer Networks", M. Kivela & M. A. Porter, arXiv:1506.00508 [physics.soc-ph]
    """

    assert len(complete_invariant_backends)>0, "No backends for complete invariants were imported!"
    if backend=="auto":
        backend=complete_invariant_backends[0]
    else:
        assert backend in complete_invariant_backends, "Backend "+str(backend)+" cannot be used to produce complete invariants"
        
    auxbuilder=auxbuilder_backends[backend]
    aux_graph=auxbuilder(net,allowed_aspects)
    return aux_graph.get_complete_invariant()



def get_automorphism_generators(net,allowed_aspects="all",include_fixed=False,backend="auto"):
    """Returns automorphism generators for the given network. The generators are permutations 
    that can be used to construct the automorphism group of the network.

    Parameters
    ----------
    net : MultilayerNetwork
       The multilayer network.
    allowed_aspects : list of ints, string
       The aspects that can be permuted in this isomorphism type. Nodes are in aspect 0 by convention.
       Value "all" will allow all permutations, i.e., it gives the (nonpartial) node-layer isomorphism.
    include_fixed : bool
       If True the elementary layer permutations include elements that remain unchanged.
    backend : string
       The program to be used for solving the graph isomorphism of the auxiliary graphs. Value "auto" 
       will select the best available candidate. For a list of backends, see documentation of the package.
    
    Returns
    -------
    automorphism_generators : list of lists of dicts
       Each element in the list is a permutation for a multilayer network. A permutation of a multilayer network
       is a list of permutations, one for each aspect. Permutation for an aspect is a dictionary where each key
       is mapped to the value. If include_fixed is not set true, the dictionaries do not contain elementary
       layers that would be mapped to themselves. 

    References
    ----------
    "Isomorphisms in Multilayer Networks", M. Kivela & M. A. Porter, arXiv:1506.00508 [physics.soc-ph]
    """

    assert len(automorphism_group_generator_backends)>0, "No backends for automorphism generators were imported!"
    if backend=="auto":
        backend=automorphism_group_generator_backends[0]
    else:
        assert backend in automorphism_group_generator_backends, "Backend "+str(backend)+" cannot be used to produce automorphism generators"
        
    auxbuilder=auxbuilder_backends[backend]
    aux_graph=auxbuilder(net,allowed_aspects)

    return aux_graph.get_automorphism_generators(include_fixed=include_fixed)



def get_isomorphism(net1,net2,allowed_aspects="all",include_fixed=False,backend="auto"):
    """Returns an isomorphism between net1 and net2 if possible.

    Parameters
    ----------
    net1 : MultilayerNetwork
       The first multilayer network.
    net2 : MultilayerNetwork
       The second multilayer network.
    allowed_aspects : list of ints, string
       The aspects that can be permuted in this isomorphism type. Nodes are in aspect 0 by convention.
       Value "all" will allow all permutations, i.e., it gives the (nonpartial) node-layer isomorphism.
    include_fixed : bool
       If True the elementary layer permutations include elements that remain unchanged.
    backend : string
       The program to be used for solving the graph isomorphism of the auxiliary graphs. Value "auto" 
       will select the best available candidate. For a list of backends, see documentation of the package.
    
    Returns
    -------
    automorphism_generators : lists of dicts, None
       A permutation of the first multilayer network that gives the second network. A permutation of a multilayer network
       is a list of permutations, one for each aspect. Permutation for an aspect is a dictionary where each key
       is mapped to the value. If include_fixed is not set true, the dictionaries do not contain elementary
       layers that would be mapped to themselves. If the two networks are not isomorphic, None is returned instead.

    References
    ----------
    "Isomorphisms in Multilayer Networks", M. Kivela & M. A. Porter, arXiv:1506.00508 [physics.soc-ph]
    """

    assert len(isomorphism_mapping_backends)>0, "No backends for isomorphism mapping were imported!"
    if backend=="auto":
        backend=isomorphism_mapping_backends[0]
    else:
        assert backend in isomorphism_mapping_backends, "Backend "+str(backend)+" cannot be used to produce isomorphism mappings"
        
    auxbuilder=auxbuilder_backends[backend]
    aux_graph1=auxbuilder(net1,allowed_aspects)
    aux_graph2=auxbuilder(net2,allowed_aspects)

    return aux_graph1.get_isomorphism(aux_graph2,include_fixed=include_fixed)
