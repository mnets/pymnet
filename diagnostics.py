from net import *

def monoplex_degs(net):
    """Returns the degree distribution of a monoplex network.
    """
    degs={}
    for node in net:
        d=net[node].deg()
        degs[d]=degs.get(d,0)+1
    return degs
