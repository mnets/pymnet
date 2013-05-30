from net import *
import math

def aggregate(net,dimensions,newNet=None,selfEdges=False):
    """ Returns a new network with reduced number of dimensions. 

    Parameters
    ----------
    net (MultisliceNetwork) : The original network
    dimensions (int,tuple) : The dimension which is aggregated over,
                             or a tuple if many dimensions
    newNet (MultisliceNetwork) : Empty network to be filled and returne.
                                 If None, a new one is created by this
                                 function.
    selfEdges (bool) : If true aggregates self-edges too

    """
    try:
        dimensions=int(dimensions)
        dimensions=(dimensions,)
    except TypeError:
        pass
    
    if newNet==None:
        newNet==MultisliceNetwork(dimensions=net.dimensions-len(dimensions),
                                  noEdge=net.noEdge,
                                  directed=net.directed)
    assert newNet.dimensions==net.dimensions-len(dimensions)
    for d in dimensions:
        assert 0<d<=net.dimensions


    for node in net:
        newNet.add_node(node)
    
    edgeIndices=filter(lambda x:math.floor(x/2) not in dimensions,range(2*net.dimensions))
    for edge in net.edges:
        newEdge=[]
        for index in edgeIndices:
            newEdge.append(edge[index])
        if selfEdges or not newEdge[0::2]==newEdge[1::2]:
            newNet[tuple(newEdge)]=newNet[tuple(newEdge)]+edge[-1]

    return newNet
