from net import MultilayerNetwork,MultiplexNetwork
import math,random

def single_layer_conf(net,degs):
    """Generates a realization of configuration model network.

    Parameters
    ----------
    net : Empty network object that is to be filled.
    deg (dict) : The degree distribution. Keys are degrees, and corresponding
                 values are number of nodes with the given degree.

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
    assert sum(map(lambda x:x[0]*x[1],degs.items()))%2==0
    stubs=[]
    selfedges={}
    multiedges=set()
    edgetoindex={}
    nodes=sum(degs.values())

    node=0
    for k,num in degs.items():
        for i in range(num):
            for j in range(k):
                stubs.append(node)
            node+=1
    random.shuffle(stubs)

    for s in range(len(stubs)/2):
        node1,node2=sorted([stubs[2*s],stubs[2*s+1]])

        edgetoindex[(node1,node2)]=edgetoindex.get((node1,node2),[])+[s]

        if net[node1,node2]!=0:
            multiedges.add((node1,node2))

        if node1==node2:
            selfedges[node1]=selfedges.get(node1,[])+[s]
        else:
            net[node1,node2]=1

    for node,sis in selfedges.items():
        for si in sis:
            repeat=True
            while repeat:
                #select two edges at random
                e1i,e2i=map(lambda x:2*x,random.sample(xrange(len(stubs)/2),2))
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
                            stubs[si],stubs[si+1]=n3,n5
                            stubs[e1i],stubs[e1i+1]=node,n2
                            stubs[e2i],stubs[e2i+1]=node,n4
                            repeat=False

    for n1,n2 in multiedges:
        for dummy in range(len(edgetoindex[(n1,n2)])/2):
            repeat=True
            while repeat:
                #select two edges at random
                e1i,e2i=map(lambda x:2*x,random.sample(xrange(len(stubs)/2),2))
                c=[n1,n2,stubs[e1i],stubs[e1i+1],stubs[e2i],stubs[e2i+1]]
                n3,n4=sorted([c[2],c[3]])
                n5,n6=sorted([c[4],c[5]])
                if len(set(c))==len(c):
                    if (n3,n4) not in multiedges and (n5,n6) not in multiedges:
                        if net[n1,n3]==0 and net[n2,n4]==0 and net[n1,n5]==0 and net[n2,n6]==0:
                            net[n1,n2]=0
                            net[n3,n4]=0
                            net[n5,n6]=0
                            net[n1,n3]=1
                            net[n2,n4]=1
                            net[n1,n5]=1
                            net[n2,n6]=1
                            si1,si2=edgetoindex[n1,n2].pop(),edgetoindex[n1,n2].pop()
                            stubs[si1],stubs[si1+1]=n1,n3
                            stubs[si1],stubs[si1+1]=n2,n4
                            stubs[e1i],stubs[e1i+1]=n1,n5
                            stubs[e2i],stubs[e2i+1]=n2,n6
                            repeat=False


def single_layer_er(net,nodes,p):
    """Efficient generation of large random networks. 
    See PRE 71, 036113 (2005) 
    """
    n=len(nodes)
    for node in nodes:
        net.add_node(node,0)
    v,w=1,-1
    while (v < n):
        r=random.random()
        w=w+1+int(math.floor(math.log(1-r)/math.log(1-p)))
        while ((w >= v) and (v < n)):
            w = w-v
            v = v+1
        if (v < n):
            net[nodes[v],nodes[w]]=1

def conf(degs,aspects=0,couplings=("categorical",1.0)):
    """Independent configuration models for fully interconnected multiplex networks.

    Parameters
    ----------
    degs (dict(s)) : If a monoplex network, then a single dict where keys are the
                     degrees and values give the number of nodes. If more aspects,
                     then degs is a sequence of same type of dictionaries.
    aspectes (int) : Number of aspects in the network, 0 or 1.
    couplings      : The coupling types of the multiplex network object.

    Returns
    -------
    net : The (multiplex) network produced with the configuration model.

    """
    if aspects==0:
        net=MultilayerNetwork(dimensions=1)
        single_layer_conf(net,degs)
    elif aspects==1:
        nodes=None
        for ldegs in degs:
            assert nodes==None or sum(ldegs.values())==nodes, "Number of nodes in layers differ."
            nodes=sum(ldegs.values())
        net=MultiplexNetwork(couplings=aspects*[couplings])
        for l,ldegs in enumerate(degs):
            net.add_node(l,1)
            single_layer_conf(net.A[l],ldegs)
    else:
        raise Exception("0 or 1 aspects, please.")

    return net


def er(n,p):
    """Multiplex Erdos-Renyi model.

    Parameters
    ----------
    n (int) : Number of nodes
    p (int or list of ints) : Connection probability.
    """
 

    if not hasattr(p,'__iter__'): #is some sequence
        net=MultilayerNetwork(dimensions=1)
        single_layer_er(net,range(n),p)
    else:
        net=MultiplexNetwork(couplings=[('categorical',1.0)])
        for l,lp in enumerate(p):
            net.add_node(l,1)
            single_layer_er(net.A[l],range(n),lp)

    return net

def er_nonoverlapping(nodes,ps):
    """Non-overlapping multiplex Erdos-Renyi network.

    Parameters
    ----------
    nodes : List of list of nodes, where each list corresponds to
            nodes in one layer.
    ps : List of edge occupation probabilities for layers
    """
    assert len(nodes)==len(ps)
    net=MultiplexNetwork(couplings=[('categorical',1.0)],globalNodes=False)
    for layer,lnodes in enumerate(nodes):
        net.add_node(layer,1)
        single_layer_er(net.A[layer],lnodes,ps[layer])
    return net

def full(nodes,layers):
    if layers==None:
        pass
    elif not hasattr(layers,'__iter__'): #is not sequence
        n=MultiplexNetwork(couplings=[('categorical',1.0)])
        for layer in range(layers):
            for node1 in range(nodes):
                for node2 in range(nodes):
                    if node1!=node2:
                        n[node1,node2,layer,layer]=1
    else:
        pass
    return n

def full_multislice(nodes,layers):
    if not hasattr(layers,'__iter__'): #is not sequence
        n=MultilayerNetwork(dimensions=2)
        for layer1 in range(layers):
            for layer2 in range(layers):
                for node1 in range(nodes):
                    for node2 in range(nodes):
                        if node1!=node2 or layer1!=layer2:
                            n[node1,node2,layer1,layer2]=1
    else:
        raise Exception("not implemented")
    return n

def er_multislice(nodes,layers,p,randomWeights=False):
    if not hasattr(layers,'__iter__'): #is not sequence
        n=MultilayerNetwork(dimensions=2)
        for layer1 in range(layers):
            for layer2 in range(layers):
                for node1 in range(nodes):
                    for node2 in range(node1+1,nodes):
                        if node1!=node2 or layer1!=layer2:
                            if random.random()<p:
                                if randomWeights:
                                    n[node1,node2,layer1,layer2]=random.random()*10
                                else:
                                    n[node1,node2,layer1,layer2]=1
    else:
        raise Exception("not implemented")
    return n
