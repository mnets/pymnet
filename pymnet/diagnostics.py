from net import *

def degs(net,degstype="distribution"):
    """Returns the degree distribution of a multilayer network.

    If the network has more than 1 aspect the degree distribution is returned for
    node-layer tuples.

    Parameters
    ----------
    net : MultilayerNetwork
       A multilayer network object.

    degstype : string
       If 'distribution', then degs dicts give the degree distributions. I.e.,
       keys are degrees, and corresponding values are number of nodes with the given degree.
       If 'nodes', then degs dicts give node degrees. I.e, keys are node names and
       corresponding values are degrees of those nodes.

    """
    if net.aspects==0:
        the_iterator=net
    else:
        the_iterator=net.iter_node_layers()
    degs={}
    if degstype=="distribution":
        for node in the_iterator:
            d=net[node].deg()
            degs[d]=degs.get(d,0)+1
    elif degstype=="nodes":
        for node in the_iterator:
            degs[node]=net[node].deg()
    else:
        raise Exception("Invalid degstype parameter.")
    return degs

def density(net):
    """Returns the density of the network.

    Density is defined as the number of edges in the network divided by the number
    of possible edges in a general multilayer network with the same set of nodes and
    layers.
    """
    if len(net)==0:
        return 0

    if net.fullyInterconnected:        
        nl=len(net.get_layers(0))
        for a in range(net.aspects):
            nl=nl*len(net.get_layers(a+1))
        if net.directed:
            pedges=nl*(nl-1)
        else:
            pedges=(nl*(nl-1))/2
            
    return len(net.edges)/float(pedges)


def multiplex_density(net):
    """Returns a dictionary of densities of each intra-layer network of a multiplex network.
    """
    assert isinstance(net,MultiplexNetwork)
    d={}
    for layer in net.iter_layers():
        d[layer]=density(net.A[layer])
    return d

def multiplex_degs(net,degstype="distribution"):
    """Returns a dictionary of degree distributions of each intra-layer network of a multiplex network.
    
    Parameters
    ----------
    net : MultiplexNetwork
       A multiplex network object.

    degstype : string
       If 'distribution', then degs dicts give the degree distributions. I.e.,
       keys are degrees, and corresponding values are number of nodes with the given degree.
       If 'nodes', then degs dicts give node degrees. I.e, keys are node names and
       corresponding values are degrees of those nodes.

    """
    assert isinstance(net,MultiplexNetwork)
    
    d={}
    for layer in net.iter_layers():
        d[layer]=degs(net.A[layer],degstype=degstype)
    return d
