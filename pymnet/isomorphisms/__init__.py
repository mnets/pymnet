
auxbuilder_backends={}
comparison_backends=[]
certificate_backends=[]

#lets try to import some backends

#try:
import nxbackend
auxbuilder_backends["nx"]=nxbackend.AuxiliaryGraphBuilderNX
#except ImportError:
#pass

#fill in the backends that are available to do various tasks
for backendname,auxbuilder in auxbuilder_backends.items():
    if auxbuilder.has_comparison:
        comparison_backends.append(backendname)
    if auxbuilder.has_certificate:
        certificate_backends.append(backendname)



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

def get_certificate(net,allowed_aspects="all",backend="auto"):
    assert len(certificate_backends)>0, "No backends for certificates were imported!"
    if backend=="auto":
        backend=certificate_backends[0]
    else:
        assert backend in certificate_backends, "Backend "+str(backend)+" does not allow certificates"
        
    auxbuilder=auxbuilder_backends[backend]
    aux_graph=auxbuilder(net,allowed_aspects)
    return aux_graph.certificate()
