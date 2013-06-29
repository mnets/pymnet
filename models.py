from net import MultisliceNetwork,CoupledMultiplexNetwork
import math,random



def er(n,p):
    """Multiplex Erdos-Renyi model.

    Parameters
    ----------
    n (int) : Number of nodes
    p (int or list of ints) : Connection probability.
    """
    def single_layer_er(net,n,p):
        """
        Efficient generation of large random networks PRE 71, 036113 (2005) 
        """
        for node in range(n):
            net.add_node(node,0)
        v,w=1,-1
        while (v < n):
            r=random.random()
            w=w+1+int(math.floor(math.log(1-r)/math.log(1-p)))
            while ((w >= v) and (v < n)):
                w = w-v
                v = v+1
            if (v < n):
                net[v,w]=1

    if not hasattr(p,'__iter__'): #is some sequence
        net=MultisliceNetwork(dimensions=1)
        single_layer_er(net,n,p)
    else:
        net=CoupledMultiplexNetwork(couplings=[('categorical',1.0)])
        for l,lp in enumerate(p):
            net.add_node(l,1)
            single_layer_er(net.A[l],n,lp)

    return net


def full(nodes,layers):
    if layers==None:
        pass
    elif not hasattr(layers,'__iter__'): #is not sequence
        n=CoupledMultiplexNetwork(couplings=[('categorical',1.0)])
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
        n=MultisliceNetwork(dimensions=2)
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
        n=MultisliceNetwork(dimensions=2)
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
