
auxbuilder_backends={}
comparison_backends=[]
complete_invariant_backends=[]

#lets try to import some backends

try:
    import nxbackend
    auxbuilder_backends["nx"]=nxbackend.AuxiliaryGraphBuilderNX
except ImportError:
    pass

try:
    import blissbackend
    auxbuilder_backends["bliss"]=blissbackend.AuxiliaryGraphBuilderBliss
except ImportError:
    pass



#fill in the backends that are available to do various tasks
for backendname,auxbuilder in auxbuilder_backends.items():
    if auxbuilder.has_comparison:
        comparison_backends.append(backendname)
    if auxbuilder.has_complete_invariant:
        complete_invariant_backends.append(backendname)



def is_isomorphic(net1,net2,allowed_aspects="all",backend="auto"):
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
    assert len(complete_invariant_backends)>0, "No backends for certificates were imported!"
    if backend=="auto":
        backend=complete_invariant_backends[0]
    else:
        assert backend in complete_invariant_backends, "Backend "+str(backend)+" cannot be used to produce complete invariants"
        
    auxbuilder=auxbuilder_backends[backend]
    aux_graph=auxbuilder(net,allowed_aspects)
    return aux_graph.get_complete_invariant()
