"""Functions for generating multilayer and multiplex networks using various network models.
"""

##### Compatibility for Python 2/3
try:
    xrange
except NameError:
    xrange = range
######

from .net import MultilayerNetwork,MultiplexNetwork
import math,random


def single_layer_conf(net,degs,degstype="distribution"):
    """Generates a realization of configuration model network.

    Parameters
    ----------
    net : MultilayerNetwork with aspects=0
       Empty network object that is to be filled.
    degs : dict 
       Degrees of the network. See degstype parameter.
    degstype : string
       If 'distribution', then degs parameter gives the degree distribution. I.e.,
       keys are degrees, and corresponding values are number of nodes with the given degree.
       If 'nodes', then degs parameter gives node degrees. I.e, keys are node names and
       corresponding values are degrees of those nodes.

    Notes
    -----
    The algorithm used here is similar to the one in article:
    B.D McKay, N.C Wormald 'Uniform Generation of Random Regular Graphs of Moderate Degree'
    Journal of Algorithms 11, pages 52-67 (1990)

    The difference between the algorithm presented in the article and the one in this
    function is that the random restarts are not implemented here. This means that the
    sampled networks are not exactly statistically uniform. However, if the degrees 
    are small compared to the number of nodes the error is likely to be small.
    """
    stubs=[]
    selfedges={}
    multiedges=set()
    edgetoindex={}

    if degstype=="distribution":
        nstubs=sum(map(lambda x:x[0]*x[1],degs.items()))
        nodes=sum(degs.values())
        shuffled_node_indices=list(range(nodes))
        random.shuffle(shuffled_node_indices)
        node=0
        for k,num in degs.items():
            if k==0:
                for i in range(num):
                    net.add_node(shuffled_node_indices[node])
                    node+=1
            else:
                for i in range(num):
                    for j in range(k):
                        stubs.append(shuffled_node_indices[node])
                    node+=1
    elif degstype=="nodes":
        nstubs=sum(degs.values())
        nodes=len(degs)
        #for node,k in degs.iteritems():
        for node in degs:
            k=degs[node]
            for i in range(k):
                stubs.append(node)
            if k==0:
                net.add_node(node)
    else:
        raise Exception("Invalid degstype: '"+str(degstype)+"'")
    
    # Here we should do the Erdos-Gallai test
    assert nstubs%2==0
    assert (nodes*(nodes-1)) >= nstubs

    random.shuffle(stubs)

    for s in range(int(len(stubs)/2)):
        node1,node2=sorted([stubs[2*s],stubs[2*s+1]])

        edgetoindex[(node1,node2)]=edgetoindex.get((node1,node2),[])+[2*s]

        if net[node1,node2]!=0:
            multiedges.add((node1,node2))

        if node1==node2:
            selfedges[node1]=selfedges.get(node1,[])+[2*s]
        else:
            net[node1,node2]=1

    for node,sis in selfedges.items():
        for si in sis:
            repeat=True
            while repeat:
                #select two edges at random
                e1i,e2i=map(lambda x:2*x,random.sample(xrange(int(len(stubs)/2)),2))
                c=[node,stubs[e1i],stubs[e1i+1],stubs[e2i],stubs[e2i+1]]
                n2,n3=sorted([c[1],c[2]])
                n4,n5=sorted([c[3],c[4]])
                if len(set(c))==len(c):
                    if (n2,n3) not in multiedges and (n4,n5) not in multiedges:
                        if net[node,n2]==0 and net[node,n4]==0 and net[n3,n5]==0:                            
                            net[n2,n3]=0
                            net[n4,n5]=0
                            net[node,n2]=1
                            net[node,n4]=1
                            net[n3,n5]=1
                            stubs[si],stubs[si+1]=sorted([n3,n5])
                            stubs[e1i],stubs[e1i+1]=sorted([node,n2])
                            stubs[e2i],stubs[e2i+1]=sorted([node,n4])
                            repeat=False

    # Uncomment to check that everything ok so far:
    #import diagnostics
    #assert sum(map(lambda x:x[0]*x[1],diagnostics.degs(net).items()))/2.+sum(map(lambda x:len(edgetoindex[x[0],x[1]])-1,multiedges))==sum(map(lambda x:x[0]*x[1],degs.items()))/2.

    #for s in range(len(stubs)/2):
    #    n1,n2=stubs[2*s],stubs[2*s+1]
    #    assert net[n1,n2]==1,str(2*s)

    for n1,n2 in multiedges:
        for dummy in range(int(math.floor(len(edgetoindex[(n1,n2)])/2.))):
            repeat=True
            while repeat:
                #select two edges at random
                e1i,e2i=map(lambda x:2*x,random.sample(xrange(int(len(stubs)/2)),2))
                c=[n1,n2,stubs[e1i],stubs[e1i+1],stubs[e2i],stubs[e2i+1]]
                n3,n4=sorted([c[2],c[3]])
                n5,n6=sorted([c[4],c[5]])
                if len(set(c))==len(c):
                    if (n3,n4) not in multiedges and (n5,n6) not in multiedges:
                        if net[n1,n3]==0 and net[n2,n4]==0 and net[n1,n5]==0 and net[n2,n6]==0:
                            if len(edgetoindex[n1,n2])==2:
                                net[n1,n2]=0
                            assert net[n3,n4]==1
                            assert net[n5,n6]==1
                            net[n3,n4]=0
                            net[n5,n6]=0
                            net[n1,n3]=1
                            net[n2,n4]=1
                            net[n1,n5]=1
                            net[n2,n6]=1
                            si1,si2=sorted([edgetoindex[n1,n2].pop(),edgetoindex[n1,n2].pop()])
                            stubs[si1],stubs[si1+1]=sorted([n1,n3])
                            stubs[si2],stubs[si2+1]=sorted([n2,n4]) #stubs[si1],stubs[si1+1]=sorted([n2,n4])
                            stubs[e1i],stubs[e1i+1]=sorted([n1,n5])
                            stubs[e2i],stubs[e2i+1]=sorted([n2,n6])
                            repeat=False



def single_layer_er(net,nodes,p=None,edges=None):
    """Generates a realization of a monoplex Erdos-Renyi network.

    Parameters
    ----------
    net : MultilayerNetwork with aspects=0
       Empty network object that is to be filled.
    nodes : iterable
       Sequence of node labels.       
    p : float
       Probability that edges is present.
    edges : int
       Number of edges that are present.

    References
    ----------
    Efficient generation of large random networks. PRE 71, 036113 (2005) 
    """

    if (p==None and edges==None) or (p!=None and edges!=None):
        raise Exception("Give one of the parameters: p or edges.")

    n=len(nodes)
    for node in nodes:
        net.add_node(node)

    if p!=None:        
        if p==1.0:
            for node1 in nodes:
                for node2 in nodes:
                    if node1!=node2:
                        net[node1,node2]=1
        else:
            v,w=1,-1
            while (v < n):
                r=random.random()
                w=w+1+int(math.floor(math.log(1-r)/math.log(1-p)))
                while ((w >= v) and (v < n)):
                    w = w-v
                    v = v+1
                if (v < n):
                    net[nodes[v],nodes[w]]=1
    else:
        for edge_index in random.sample(xrange(int((n*(n-1))/2)),edges):
            v=int(1+math.floor(-0.5+math.sqrt(0.25+2*edge_index)))
            w=edge_index-int((v*(v-1))/2)
            net[nodes[v],nodes[w]]=1

def conf(degs,degstype="distribution",couplings=("categorical",1.0)):
    """Independent configuration model for multiplex networks.

    Parameters
    ----------
    degs : dict, dict of dicts, list of dicts, MultiplexNetwork, MultilayerNetwork
       Degrees. If dict, a monoplex network is returned. If dict of dicts, a multiplex network with
       keys as layer names is returned. If list of dicts, then a multiplex network with a layer for
       each element in the list is returned. See degstype parameter for the description of the dict
       used for describing intra-layer networks. If MultiplexNetwork (with 1 aspect) or MultilayerNetwork 
       (with 0 aspects) object is given then a copy of that network is produced with configuration
       model.

    degstype : string
       If 'distribution', then degs dicts give the degree distributions. I.e.,
       keys are degrees, and corresponding values are number of nodes with the given degree.
       If 'nodes', then degs dicts give node degrees. I.e, keys are node names and
       corresponding values are degrees of those nodes.

    couplings : tuple
       The coupling types of the multiplex network object.

    Returns
    -------
    net : MultiplexNetwork
       The (multiplex) network produced with the configuration model.


    See also
    --------
    single_layer_conf : the function used to generate a network on each layer


    """
    if isinstance(degs,MultiplexNetwork):
        assert degs.aspects==1
        d={}
        for layer in degs.iter_layers():
            dd={}
            d[layer]=dd
            for node in degs.A[layer]:
                dd[node]=degs.A[layer][node].deg()
        return conf(d,degstype="nodes")
    elif isinstance(degs,MultilayerNetwork):
        assert degs.aspects==0
        d={}
        for node in degs:
            d[node]=degs[node].deg()
        return conf(d,degstype="nodes")
    #elif isinstance(degs,dict) and not isinstance(degs.itervalues().next(),dict):
    elif isinstance(degs,dict) and not isinstance(degs[(k for k in degs).send(None)],dict):
        net=MultilayerNetwork(aspects=0)
        single_layer_conf(net,degs,degstype=degstype)
    else:        
        #check if the network is going to be node-aligned
        namedlayers=isinstance(degs,dict)
        if namedlayers:
            degslist=degs.values()
        else:
            degslist=degs
        nnodes=None
        nodeAligned=True
        if degstype=="distribution":
            for ldegs in degslist:
                lnnodes=sum(ldegs.values())
                if nnodes!=None and lnnodes!=nnodes:
                    nodeAligned=False
                nnodes=lnnodes
        elif degstype=="nodes":
            for ldegs in degslist:
                lnnodes=set(ldegs.keys())
                if nnodes!=None and lnnodes!=nnodes:
                    nodeAligned=False
                nnodes=lnnodes
        else:
            raise Exception()

        net=MultiplexNetwork(couplings=[couplings],fullyInterconnected=nodeAligned)
        if namedlayers:
            #layers=degs.iteritems()
            layers = ((node, degs[node]) for node in degs )
        else:
            layers=enumerate(degs)
        for l,ldegs in layers:
            net.add_layer(l)
            single_layer_conf(net.A[l],ldegs,degstype=degstype)

    return net


def er(n,p=None,edges=None):
    """Multiplex Erdos-Renyi model.

    Parameters
    ----------
    n : int, list of lists of nodes
       Number of nodes, or lists of nodes in each layer if network is not fully 
       interconnected.
    p : float or list of floats
       Connection probability, or list of connection probabilities for each layer.
    edges : int or list of int
       Number of edges, or list of number of edges in each layer.

    Returns
    -------
    net : MultiplexNetwork
       The (multiplex) network produced.

    See also
    --------
    single_layer_er : the function used to generate a network on each layer
    """
    # What kind of network?
    fic = not hasattr(n,'__iter__') #fully interconnected
    monoplex = (not hasattr(p,'__iter__')) and (not hasattr(edges,'__iter__')) and fic
 
    # Sanity check for parameters
    if (p==None and edges==None) or (p!=None and edges!=None):
        raise Exception("Give one of the parameters: p or edges.")
    if not fic:
        if hasattr(p,'__iter__'):
            assert len(n)==len(p)
        elif hasattr(edges,'__iter__'):
            assert len(n)==len(edges)

    
    # Create the network
    if monoplex:
        net=MultilayerNetwork(aspects=0)
    else:
        net=MultiplexNetwork(couplings=[('categorical',1.0)],fullyInterconnected=fic)
        if not hasattr(n,'__iter__'):
            if p!=None:
                nodes=list(map(lambda x:xrange(n),p))
                layers=xrange(len(p))
            else:
                nodes=list(map(lambda x:xrange(n),edges))
                layers=xrange(len(edges))
        else:
            nodes=n
            layers=xrange(len(n))
            if p!=None and (not hasattr(p,'__iter__')):
                p=list(map(lambda x:p,layers))
            if edges!=None and (not hasattr(edges,'__iter__')):
                edges=list(map(lambda x:edges,layers))
                

    # Fill in the edges
    if p!=None:
        if monoplex:
            single_layer_er(net,range(n),p=p)
        else:
            for l,lp,lnodes in zip(layers,p,nodes):
                net.add_layer(l)
                single_layer_er(net.A[l],lnodes,p=lp)
    else:
        if monoplex:
            single_layer_er(net,range(n),edges=edges)
        else:
            for l,ledges,lnodes in zip(layers,edges,nodes):
                net.add_layer(l)
                single_layer_er(net.A[l],lnodes,edges=ledges)

    return net

def er_partially_interconnected(nodes,ps,couplings=('categorical',1.0)):
    """Generate multiplex Erdos-Renyi network which is not fully interconnected.

    The produced multiplex network has a single aspect.

    Parameters
    ----------
    nodes : list of lists 
       List of lists of nodes, where each list corresponds to
       nodes in one layer.
    ps : list
       List of edge occupation probabilities for layers
    couplings : tuple
       The coupling types of the multiplex network object.

    Returns
    -------
    net : MultiplexNetwork
       The multiplex network that is produced.    
    """
    assert len(nodes)==len(ps)
    net=MultiplexNetwork(couplings=[couplings],fullyInterconnected=False)
    for layer,lnodes in enumerate(nodes):
        net.add_layer(layer)
        single_layer_er(net.A[layer],lnodes,ps[layer])
    return net

def full(nodes,layers,couplings=('categorical',1.0)):
    """Generate a full multiplex network.

    The produced multiplex network has a single aspect and is fully
    interconnected. Can also produce a full monoplex network.

    Parameters
    ----------
    nodes : int
       Number of nodes in the network
    layers : int, sequence or None
       Number of layers in the network, a sequence of layer names, or
       None for monoplex networks.
    couplings : tuple
       The coupling types of the multiplex network object.

    Returns
    -------
    net : MultiplexNetwork or MultilayerNetwork
       The multiplex network that is produced, or the monoplex
       network (which is of type MultilayerNetwork).
    """
    if layers==None:
        n=MultilayerNetwork(aspects=0)
        for node1 in range(nodes):
            for node2 in range(nodes):
                if node1!=node2:
                    n[node1,node2]=1
    elif not hasattr(layers,'__iter__'): #is not sequence
        n=MultiplexNetwork(couplings=[couplings])
        for layer in range(layers):
            for node1 in range(nodes):
                for node2 in range(nodes):
                    if node1!=node2:
                        n[node1,node2,layer,layer]=1
    else: #it's a sequence
        n=MultiplexNetwork(couplings=[couplings])
        for layer in layers:
            for node1 in range(nodes):
                for node2 in range(nodes):
                    if node1!=node2:
                        n[node1,node2,layer,layer]=1

    return n

def full_multilayer(nodes,layers):
    """Generate a full multilayer network.

    The generated network has a single aspect, and all the inter-layer 
    and intra-layer edges.

    Parameters
    ----------
    nodes : int
       Number of nodes in the network
    layers : int or sequence
       Number of layers in the network, or a sequence of layer names

    Returns
    -------
    net : MultilayerNetwork
       The multilayer network that is produced.
    """
    if not hasattr(layers,'__iter__'): #is not sequence
        layers=range(layers)

    n=MultilayerNetwork(aspects=1)
    for layer1 in layers:
        for layer2 in layers:
            for node1 in range(nodes):
                for node2 in range(nodes):
                    if node1!=node2 or layer1!=layer2:
                        n[node1,node2,layer1,layer2]=1
    return n

def er_multilayer(nodes,layers,p,randomWeights=False):
    """Generate multilayer Erdos-Renyi network.

    The produced multilayer network has a single aspect.

    Parameters
    ----------
    nodes : int
       Number of nodes in the network
    layers : int or sequence
       Number of layers in the network, or a sequence of layer names
    p : float
       The edge probability
    randomWeights : bool
       If true the weights are uniformly random between (0,1].

    Returns
    -------
    net : MultilayerNetwork
       The multilayer network that is produced.
    """


    if not hasattr(layers,'__iter__'): #is not sequence
        layers=range(layers)

    n=MultilayerNetwork(aspects=1)
    for layer1 in layers:
        for layer2 in layers:
            for node1 in range(nodes):
                for node2 in range(node1+1,nodes):
                    if node1!=node2 or layer1!=layer2:
                        if random.random()<p:
                            if randomWeights:
                                n[node1,node2,layer1,layer2]=random.random()
                            else:
                                n[node1,node2,layer1,layer2]=1

    return n





def conf_overlaps(ol_degs, couplings=None):
    """
    Generate multiplex configuration model network with given overlap degree 
    sequences. 

    One can specify the 'overlap degree sequences', as defined in overlap_degs.
    
    Parameters
    ----------
    ol_degs : dict of dicts
        The overlap degrees. Keys are tuples containing layer combinations 
        (including the trivial combination of a single layer) and 
        values are the overlap degree distributions with nodes as keys. See
        overlap_degs.
    couplings : None or tuple
        The coupling types passed directly to multiplex network object
        constructor.
    
    Returns
    -------
    net : MultiplexNetwork
       The multiplex network produced with the configuration model.
       

    Notes
    -----
    The algorithm to produce the multiplex network is a modified version of the
    one implemented in single_layer_conf (McKay et al). The modification tries
    link swapping in cases where edges in another layer combination already 
    exists.
    

    References
    ----------
    Marceau, Vincent, et al. "Modeling the dynamical interaction between 
    epidemics on overlay networks." Physical Review E 84.2 (2011): 026105.
    """
    
    net = MultiplexNetwork(couplings=couplings)
    used_edges = set()
    
    for layer_comb in ol_degs:
        degs = ol_degs[layer_comb]
        
        # mostly modified from single_layer_conf
        stubs=[]
        selfedges={}
        multiedges=set()
        takenedges=set()
        edgetoindex={}
        
        net_temp = MultilayerNetwork()
        
        nstubs=sum(degs.values())
        n_nodes=len(degs)
        for node in degs:
            k=degs[node]
            for i in range(k):
                stubs.append(node)
            if k==0:
                net_temp.add_node(node)
                
        # Here we should do the Erdos-Gallai test
        assert nstubs%2==0
        assert (n_nodes*(n_nodes-1)) >= nstubs
    
        random.shuffle(stubs)
        
        for s in range(int(len(stubs)/2)):
            node1,node2=sorted([stubs[2*s],stubs[2*s+1]])
    
            edgetoindex[(node1,node2)]=edgetoindex.get((node1,node2),[])+[2*s]
    
            if node1==node2:
                selfedges[node1]=selfedges.get(node1,[])+[2*s]
            elif net_temp[node1,node2]!=0:
                multiedges.add((node1,node2))
            elif (node1, node2) in used_edges:
                takenedges.add((node1,node2))
            else:
                net_temp[node1,node2]=1
                used_edges.add((node1, node2))
                
        for node,sis in selfedges.items():
            for si in sis:
                repeat=True
                while repeat:
                    #select two edges at random
                    e1i,e2i=map(lambda x:2*x,random.sample(xrange(int(len(stubs)/2)),2))
                    c=[node,stubs[e1i],stubs[e1i+1],stubs[e2i],stubs[e2i+1]]
                    n2,n3=sorted([c[1],c[2]])
                    n4,n5=sorted([c[3],c[4]])
                    if len(set(c))==len(c):
                        if (n2,n3) not in multiedges and (n4,n5) not in multiedges and (n2,n3) not in takenedges and (n4,n5) not in takenedges:
                            e1 = tuple(sorted([node, n2]))
                            e2 = tuple(sorted([node, n4]))
                            e3 = tuple(sorted([n3, n5]))
                            if e1 not in used_edges and e2 not in used_edges and e3 not in used_edges:
                                net_temp[n2,n3]=0
                                net_temp[n4,n5]=0
                                net_temp[node,n2]=1
                                net_temp[node,n4]=1
                                net_temp[n3,n5]=1
                                stubs[si],stubs[si+1]=sorted([n3,n5])
                                stubs[e1i],stubs[e1i+1]=sorted([node,n2])
                                stubs[e2i],stubs[e2i+1]=sorted([node,n4])
                                repeat=False
                                
                                used_edges.remove((n2,n3))
                                used_edges.remove((n4,n5))
                                used_edges.add(e1)
                                used_edges.add(e2)
                                used_edges.add(e3)
                                
        for n1,n2 in multiedges:
            for dummy in range(int(math.floor(len(edgetoindex[(n1,n2)])/2.))):
                repeat=True
                while repeat:
                    #select two edges at random
                    e1i,e2i=map(lambda x:2*x,random.sample(xrange(int(len(stubs)/2)),2))
                    c=[n1,n2,stubs[e1i],stubs[e1i+1],stubs[e2i],stubs[e2i+1]]
                    n3,n4=sorted([c[2],c[3]])
                    n5,n6=sorted([c[4],c[5]])
                    if len(set(c))==len(c):
                        if (n3,n4) not in multiedges and (n5,n6) not in multiedges and (n3,n4) not in takenedges and (n5,n6) not in takenedges:
                            e1 = tuple(sorted([n1,n3]))
                            e2 = tuple(sorted([n2,n4]))
                            e3 = tuple(sorted([n1,n5]))
                            e4 = tuple(sorted([n2,n6]))
                            if e1 not in used_edges and e2 not in used_edges and e3 not in used_edges and e4 not in used_edges: #net[n1,n3]==0 and net[n2,n4]==0 and net[n1,n5]==0 and net[n2,n6]==0:
                                if len(edgetoindex[n1,n2])==2:
                                    net_temp[n1,n2]=0
                                    used_edges.remove((n1,n2))
                                net_temp[n3,n4]=0
                                net_temp[n5,n6]=0
                                net_temp[n1,n3]=1
                                net_temp[n2,n4]=1
                                net_temp[n1,n5]=1
                                net_temp[n2,n6]=1
                                si1,si2=sorted([edgetoindex[n1,n2].pop(),edgetoindex[n1,n2].pop()])
                                stubs[si1],stubs[si1+1]=sorted([n1,n3])
                                stubs[si2],stubs[si2+1]=sorted([n2,n4])#stubs[si1],stubs[si1+1]=sorted([n2,n4])
                                stubs[e1i],stubs[e1i+1]=sorted([n1,n5])
                                stubs[e2i],stubs[e2i+1]=sorted([n2,n6])
                                repeat=False
                                
                                used_edges.remove((n3,n4))
                                used_edges.remove((n5,n6))
                                used_edges.add(e1)
                                used_edges.add(e2)
                                used_edges.add(e3)
                                used_edges.add(e4)
                                
        for n1,n2 in takenedges:
            for si1 in edgetoindex[(n1,n2)]:
                repeat=True
                while repeat:
                    #select two edges at random
                    e1i,e2i=map(lambda x:2*x,random.sample(xrange(int(len(stubs)/2)),2))
                    c=[n1,n2,stubs[e1i],stubs[e1i+1],stubs[e2i],stubs[e2i+1]]
                    n3,n4=sorted([c[2],c[3]])
                    n5,n6=sorted([c[4],c[5]])
                    if len(set(c))==len(c):
                        if (n3,n4) not in takenedges and (n5,n6) not in takenedges:
                            e1 = tuple(sorted([n1,n3]))
                            e2 = tuple(sorted([n2,n5]))
                            e3 = tuple(sorted([n4,n6]))
                            if e1 not in used_edges and e2 not in used_edges and e3 not in used_edges:
                                assert net_temp[n3,n4]==1
                                assert net_temp[n5,n6]==1
                                net_temp[n3,n4]=0
                                net_temp[n5,n6]=0
                                net_temp[n1,n3]=1
                                net_temp[n2,n5]=1
                                net_temp[n4,n6]=1
                                
                                stubs[si1],stubs[si1+1]=sorted([n1,n3])
                                stubs[e1i],stubs[e1i+1]=sorted([n2,n5])
                                stubs[e2i],stubs[e2i+1]=sorted([n4,n6])
                                repeat=False
                                
                                used_edges.remove((n3,n4))
                                used_edges.remove((n5,n6))
                                used_edges.add(e1)
                                used_edges.add(e2)
                                used_edges.add(e3)
                                
        for e in net_temp.edges:
            for layer in layer_comb:
                net[e[0], e[1], layer] = 1
                                    
    return net


def er_overlaps_match_aggregated(n, edges, ps, couplings=None):
    '''
    Generates a multiplex Erdos-Renyi networks which produces an aggregated
    network with given number of edges. The target it that the aggregated 
    network of the resulting network has edges * n_layers edges.
    
    The algorithm goes through each of the user-given layer combinations with
    2 or more layers. It generates an ER graph which does not include any edges
    that are already in any of the layers of the combination. It then copies
    the edges of that ER graph to all of the layers of the combination.

    


    Parameters
    ----------
    n : int
        Number of nodes
    edges : int
        Number of edges in each layer
    ps : dict
        Proportions of overlapping edges in each layer combination given as 
        keys (note that the sum of these proportions should not exceed 1 for 
        any one layer). The trivial combinations including only a single layer
        do not need to be given (and if they are given, the given proportions
        are ignored).
    couplings : None or tuple
        The coupling types of the multiplex network object.

    Returns
    -------
    net : MultiplexNetwork
       The multiplex network produced
    '''
    
    net = MultiplexNetwork(couplings=couplings)
    used_edges = set()
    
    e_left = {}
    for layer_comb in ps:
        if len(layer_comb) == 1:
            e_left[layer_comb[0]] = e_left.get(layer_comb[0], edges)
            continue
        p = ps[layer_comb]
        m = int(round(p*edges))
        k = len(layer_comb)
        if k > 1:
            for layer in layer_comb:
                e_left[layer] = e_left.get(layer, edges) - m
            i = 0
            while i < (k * m):
                edge_index = random.choice(xrange(int((n*(n-1))/2)))
                v=int(1+math.floor(-0.5+math.sqrt(0.25+2*edge_index)))
                w=edge_index-int((v*(v-1))/2)
                edge = (w, v)
                if edge not in used_edges:
                    used_edges.add(edge)
                    i += 1
                    for layer in layer_comb:
                        net[edge[0], edge[1], layer] = 1
                        
    for layer in e_left:
        m = e_left[layer]
        i = 0
        while i < m:
            edge_index = random.choice(xrange(int((n*(n-1))/2)))
            v=int(1+math.floor(-0.5+math.sqrt(0.25+2*edge_index)))
            w=edge_index-int((v*(v-1))/2)
            edge = (w, v)
            if edge not in used_edges:
                used_edges.add(edge)
                i += 1
                net[edge[0], edge[1], layer] = 1
    
    return net

    
def ba_total_degree(n, ms, couplings=None):
    """
    Generates a Barabasi-Albert multiplex network, where the preferential
    attachment process is run for each layer separately and concurrently
    in a way that the total degree of the node is used for the preferential
    attachment. That is, the new nodes attach preferentially to nodes that
    have high total degree (sum of degree in all layers).
    
    Parameters
    ----------
    n : int
        number of nodes
    ms : list of ints
        the numbers of links added to each new node for each layer
    couplings : None or tuple
        The coupling types of the multiplex network object.
        
    Returns
    -------
    net : MultiplexNetwork
       The multiplex network produced
       
    References
    ----------
    Kim, Jung Yeol, and K-I. Goh. "Coevolution and correlated multiplexity in 
    multiplex networks." Physical review letters 111.5 (2013): 058702.
    """
    
    net = MultiplexNetwork(couplings=couplings)
    links = []
    
    for i in range(n):
        net.add_node(i)
        link_sets = []
        for layer, m in enumerate(ms):
            if i == m:
                link_set = set(range(i))
                
            elif i > m:
                link_set = set()
                while len(link_set) < m:
                    link_set = link_set | set(random.sample(links, m - len(link_set)))
                    
            else:
                link_set = set()
                    
            link_sets.append(link_set)
            
            for j in link_set:
                net[i,j,layer] = 1
            
        for link_set in link_sets:
            links += list(link_set)
            links += [i]*(len(link_set))
            
    return net


try:
    from . import nxwrap as nx
    import networkx

    def ws(n, edges, p=0.3, couplings=None):
        """
        Generates a multiplex network where each layer is generated
        using the same Watts-Strogatz model. 

        Parameters
        ----------
        n : int
            Number of nodes
        edges : list of ints
            Number of edges in each layer
        p : float
            Probability of rewiring an edge
        couplings : None or tuple
            The coupling types of the multiplex network object.

        Returns
        -------
        net : MultiplexNetwork
           The multiplex network produced
        """

        net = MultiplexNetwork(couplings=couplings)
        for layer, m in enumerate(edges):
            net.add_layer(layer)
            net.A[layer] = nx.watts_strogatz_graph(n, int(math.ceil(2*m / float(n))), p=p)

        return net
    
    
    def geo(n, edges, couplings=None):
        """
        Generates a multiplex network where each layer is generated using the
        same soft geometric network model.

        The intra-layer networks are generated using the networkx function
        soft_random_geometeric_graph.
        
        Parameters
        ----------
        n : int
            Number of nodes
        edges : list of ints
            Approximate number of edges in each layer
        couplings : None or tuple
            The coupling types of the multiplex network object.

        Returns
        -------
        net : MultiplexNetwork
           The multiplex network produced

        Notes
        -----
        Works only with networkX2
        """

        net = MultiplexNetwork(couplings=couplings)
        pos = None
        for layer, m in enumerate(edges):
            net.add_layer(layer)
            r = math.sqrt(2.2 * float(m) / ((n - 1.0) * n) / math.pi)
            netX = networkx.soft_random_geometric_graph(n, r, pos=pos)
            pos = networkx.get_node_attributes(netX, 'pos')
            for node in netX.nodes:
                net.add_node(node)

            for e in netX.edges:
                net[e[0], e[1], layer] = 1

        return net
except ImportError:
    pass
