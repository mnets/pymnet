"""Functions taking in networks and returning transformed versions of them.
"""
import math
import itertools
import random
from functools import reduce

#from . import net as netmodule #this will break the circular imports
#import net as netmodule #this will not work in python 3
import pymnet as netmodule #this is the solution



def aggregate(net,aspects,newNet=None,selfEdges=False):
    """Reduces the number of aspects by aggregating them.

    This function aggregates edges from multilayer aspects together
    by summing their weights. Any number of aspects is allowed, and the
    network can have non-diagonal inter-layer links. The layers cannot 
    be weighted such that they would have different coefficients when 
    the weights are summed together.

    Note that no self-links are created and all the inter-layer links
    are disregarded.

    Parameters
    ----------
    net : MultilayerNetwork
       The original network.
    aspects : int or tuple 
       The aspect which is aggregated over,or a tuple if many aspects
    newNet : MultilayerNetwork 
       Empty network to be filled and returned. If None, a new one is 
       created by this function.
    selfEdges : bool 
       If true aggregates self-edges too

    Returns
    -------
    net : MultiplexNetwork
       A new instance of multiplex network which is produced.

    Examples
    --------
    Aggregating the network with a singe aspect can be done as follows:

    >>> n=net.MultiplexNetwork([('categorical',1.0)])
    >>> an=transforms.aggregate(n,1)

    You need to choose which aspect(s) to aggregate over if the network 
    has multiple aspects:

    >>> n=MultiplexNetwork([2*('categorical',1.0)])
    >>> an1=transforms.aggregate(n,1)
    >>> an2=transforms.aggregate(n,2)
    >>> an12=transforms.aggregate(n,(1,2))
    """
    try:
        aspects=int(aspects)
        aspects=(aspects,)
    except TypeError:
        pass
    
    if newNet==None:
        newNet=netmodule.MultilayerNetwork(aspects=net.aspects-len(aspects),
                                 noEdge=net.noEdge,
                                 directed=net.directed,
                                 fullyInterconnected=net.fullyInterconnected)
    assert newNet.aspects==net.aspects-len(aspects)
    for d in aspects:
        assert 0<d<=(net.aspects+1)

    #Add nodes
    for node in net:
        newNet.add_node(node)
    
    #Add edges
    edgeIndices=list(filter(lambda x:math.floor(x/2) not in aspects,range(2*(net.aspects+1))))
    for edge in net.edges:
        newEdge=[]
        for index in edgeIndices:
            newEdge.append(edge[index])
        if selfEdges or not newEdge[0::2]==newEdge[1::2]:
            newNet[tuple(newEdge)]=newNet[tuple(newEdge)]+edge[-1]

    #Add node-layer tuples (if not node-aligned)
    if not net.fullyInterconnected and newNet.aspects>0:
        nodeIndices=list(filter(lambda x:x not in aspects,range(1,net.aspects+1)))
        for nlt in net.iter_node_layers():
            newlayer=[]
            for a in nodeIndices:
                newlayer.append(nlt[a])
            #we need to use the public interface for adding nodes which means that
            #layers are only given as tuples for multi-aspect networks
            if len(newlayer)==1: 
                newNet.add_node(nlt[0],layer=newlayer[0])
            else:
                newNet.add_node(nlt[0],layer=newlayer)

    return newNet


def overlay_network(net):
    """Returns the overlay network of a multilayer network with 1 aspect.

    Returns
    -------
    net : MultiplexNetwork
       A new instance of multiplex network which is produced.
    """
    assert net.aspects==1
    newnet=netmodule.MultilayerNetwork()
    for layer in net.slices[1]:
        for node1 in net.slices[0]:
            for node2 in net.slices[0]:
                if net.directed or node1>node2:
                    newnet[node1,node2]=newnet[node1,node2]+net[node1,node2,layer,layer]
    return newnet

def subnet(net,nodes,*layers,**kwargs):
    """Returns an induced subgraph with given set of nodes and layers.

    Parameters
    ----------
    net : MultilayerNetwork, MultiplexNetwork 
        The original network.
    nodes : sequence
        The nodes that span the induces subgraph.
    *layers : *sequence
        (Elementary) layers included in the subgraph. One parameter for each aspect.
    newNet : None, MultilayerNetwork, MultiplexNetwork    
        An empty new network or None. If None, the new network is created as a
        an empty copy of the net. The edges and nodes are copied to this network.
    nolinks : bool
        If set True, this function does not copy any links. That is, the returned
        network is _not_ an induced subnetwork but an empty network.

    Return
    ------
    subnet : type(net), or type(newNet)
        The induced subgraph that contains only nodes given in
        `nodes` and the edges between those nodes that are
        present in `net`. Node properties etc are left untouched.
    """

    if "newNet" in kwargs:
        newNet=kwargs["newNet"]
    else:
        newNet=None

    if "nolinks" in kwargs:
        nolinks=kwargs["nolinks"]
    else:
        nolinks=False

    assert len(layers)==net.aspects, "Please give layers for each aspect."
    nodelayers=[]
    for a,elayers in enumerate(itertools.chain([nodes],layers)):
        if elayers==None:
            nodelayers.append(set(net.get_layers(a)))
        else:
            nodelayers.append(set(elayers))

    if newNet==None:
        if isinstance(net,netmodule.MultiplexNetwork):
            newNet=netmodule.MultiplexNetwork(couplings=net.couplings,
                                    directed=net.directed,
                                    noEdge=net.noEdge,
                                    fullyInterconnected=net.fullyInterconnected)
        elif isinstance(net,netmodule.MultilayerNetwork):
            newNet=netmodule.MultilayerNetwork(aspects=net.aspects,
                                     noEdge=net.noEdge,
                                     directed=net.directed,
                                     fullyInterconnected=net.fullyInterconnected)
        else:
            raise Exception("Invalid net type: "+str(type(net)))
            
    if not net.fullyInterconnected and newNet.fullyInterconnected:
        raise TypeError("Cannot copy a non-fully-interconnected network to a fully interconnected network.")

    addedElementaryLayers=[]
    for a,elayers in enumerate(nodelayers):#enumerate(itertools.chain((nodes,),layers)):
        if net.fullyInterconnected or a!=0:
            addedElementaryLayers.append(0)
            oldElementaryLayers=net.get_layers(a)
            for elayer in elayers:
                if elayer in oldElementaryLayers:
                    newNet.add_layer(elayer,a)
                    addedElementaryLayers[-1]+=1

    if not newNet.fullyInterconnected:
        totalNodeLayers=0
        for nl in net.iter_node_layers():
            if reduce(lambda x,y:x and y, (e in nodelayers[a] for a,e in enumerate(nl))):
                if net.aspects==1:
                    newNet.add_node(nl[0],layer=nl[1])
                else:
                    newNet.add_node(nl[0],layer=nl[1:])
                totalNodeLayers+=1
    else:
        totalNodeLayers=reduce(lambda x,y:x*y,addedElementaryLayers)


    #copy the links
    if not nolinks:        
        if isinstance(net,netmodule.MultiplexNetwork) and isinstance(newNet,netmodule.MultiplexNetwork):
            #Go through all the combinations of new layers
            for layer in itertools.product(*nodelayers[1:]):
                layer=layer[0] if net.aspects==1 else layer
                subnet(net.A[layer],nodelayers[0],newNet=newNet.A[layer],nolinks=nolinks)
        elif (isinstance(net,netmodule.MultilayerNetwork) and (isinstance(newNet,netmodule.MultilayerNetwork) and not isinstance(newNet,netmodule.MultiplexNetwork))) or (isinstance(net,netmodule.MultiplexNetwork) and (isinstance(newNet,netmodule.MultilayerNetwork) and not isinstance(newNet,netmodule.MultiplexNetwork))):
            for nl1 in itertools.product(*nodelayers):
                nl1 = nl1[0] if net.aspects==0 else nl1
                if net[nl1].deg()>=totalNodeLayers:
                    for nl2 in itertools.product(*nodelayers):
                        nl2 = nl2[0] if net.aspects==0 else nl2
                        if net[nl1][nl2]!=net.noEdge:
                            newNet[nl1][nl2]=net[nl1][nl2]
                else:
                    if net.aspects==0:
                        for nl2 in net[nl1]:
                            if nl2 in nodelayers[0]:
                                newNet[nl1][nl2]=net[nl1][nl2]
                    else:
                        for nl2 in net[nl1]:
                            if reduce(lambda x,y:x and y, (e in nodelayers[a] for a,e in enumerate(nl2))):
                                newNet[nl1][nl2]=net[nl1][nl2]
        elif isinstance(net,netmodule.MultilayerNetwork) and isinstance(newNet,netmodule.MultiplexNetwork):
            raise TypeError("Cannot copy multilayer network to multiplex network.")
        else:
            raise TypeError("Invalid net types: "+str(type(net))+ " and "+ str(type(newNet)))

    return newNet


def supra_adjacency_matrix(net,includeCouplings=True):
    """Returns the supra-adjacency matrix and a list of node-layer pairs.

    Parameters
    ----------
    includeCoupings : bool
       If True, the inter-layer edges are included, if False, only intra-layer
       edges are included.

    Returns
    -------
    matrix, nodes : numpy.matrix, list
       The supra-adjacency matrix and the list of node-layer pairs. The order
       of the elements in the list and the supra-adjacency matrix are the same.
    """

    return net.get_supra_adjacency_matrix(includeCouplings=includeCouplings)

def relabel(net,nodeNames=None,layerNames=None):
    """Returns a copy of the network with nodes and layers relabeled.
    
     Parameters
     ----------
     net : MultilayerNetwork, or MultiplexNetwork 
        The original network.
     nodeNames : None, or dict
        The map from node names to node indices.
     layerNames : None, dict, or sequence of dicts
        The map(s) from (elementary) layer names to (elementary) layer indices.
        Note that you can add empty dicts for aspects you do not want to relabel.

     Return
     ------
     newnet : type(net)
         The normalized network.
    """
    def dget(d,e):
        if e in d:
            return d[e]
        else:
            return e

    def layer_to_indexlayer(layer,layerNames):
        return tuple([dget(layerNames[i],elayer) for i,elayer in enumerate(layer)])

    if nodeNames==None:
        nodeNames={}

    if layerNames==None:
        layerNames=[]

    if net.aspects==1:
        if isinstance(layerNames,dict):
            layerNames=[layerNames]

    for aspect in range(net.aspects):
        if len(layerNames)<aspect+1:
            layerNames.append({})
     
    if type(net)==netmodule.MultilayerNetwork:
        newNet=netmodule.MultilayerNetwork(aspects=net.aspects,
                                 noEdge=net.noEdge,
                                 directed=net.directed,
                                 fullyInterconnected=net.fullyInterconnected)
    elif type(net)==netmodule.MultiplexNetwork:
        newNet=netmodule.MultiplexNetwork(couplings=net.couplings,
                                directed=net.directed,
                                noEdge=net.noEdge,
                                fullyInterconnected=net.fullyInterconnected)
    else:
        raise Exception("Invalid type of net",type(net))

    for node in net:
        newNet.add_node(dget(nodeNames,node))
    for aspect in range(net.aspects):
        for layer in net.slices[aspect+1]:
            newNet.add_layer(dget(layerNames[aspect],layer),aspect=aspect+1) 

    if not net.fullyInterconnected:
        for nodelayer in net.iter_node_layers():
            layer=layer_to_indexlayer(nodelayer[1:],layerNames)
            if net.aspects==1:
                layer=layer[0]
            newNet.add_node(dget(nodeNames,nodelayer[0]),layer=layer)

    if type(net)==netmodule.MultilayerNetwork:
        for edge in net.edges:
            newedge=[dget(nodeNames,edge[0]),dget(nodeNames,edge[1])]
            for aspect in range(net.aspects):
                newedge.append(dget(layerNames[aspect],edge[2+aspect*2]))
                newedge.append(dget(layerNames[aspect],edge[2+aspect*2+1]))
            newNet[tuple(newedge)]=edge[-1]
    elif type(net)==netmodule.MultiplexNetwork:
            for layer in net.iter_layers():
                if net.aspects==1:
                    layertuple=(layer,)
                else:
                    layertuple=layer
                for node in net.A[layer]:
                    for neigh in net.A[layer][node]:
                        newNet[(dget(nodeNames,node),dget(nodeNames,neigh))+layer_to_indexlayer(layertuple,layerNames)]=net[(node,neigh)+layertuple]

                            
    return newNet

def normalize(net,nodesToIndices=None,layersToIndices=None,nodeStart=0,layerStart=0):
    """Returns a copy of the network with layer and node indices as integers.

    In network with n nodes the nodes are renamed so that they run from 0 to n-1.
    In network has b_a elementary layers in aspect a, the layers are renamed so 
    that they run from 0 to b_a-1.

    Parameters
    ----------
    net : MultilayerNetwork, or MultiplexNetwork 
       The original network.
    nodesToIndices : None, or bool
       True returns the map from node names to node indices, False returns the map from 
       node indices to node names, and None doesn't return anything.
    layersToIndices : None, or bool
       True returns the map(s) from (elementary) layer names to (elementary) layer indices,
       False returns the map(s) from (elementary) layer indices to (elementary) layer names,
       and None doesn't return anything.
    nodeStart : int
       The indexing for nodes starts from this value.
    layerStart : int
       The indexing for layers starts from this value.

    Return
    ------
    newnet : type(net)
        The normalized network.
    (optional) nodeNames : dict
        The map from node names/indices to node indices/names.
    (optional) layerNames : dict, or list of dicts
        The map(s) from (elementary) layer names/indices to (elementary) layer indices/names. One
        map for each aspect.
    """
  
    nodeNames={}
    layerNames=[{} for aspect in range(net.aspects)]

    for i,node in enumerate(sorted(net)):
        nodeNames[node]=i+nodeStart
    for aspect in range(net.aspects):
        for i,layer in enumerate(sorted(net.slices[aspect+1])):
            layerNames[aspect][layer]=i+layerStart

    newNet=relabel(net,nodeNames=nodeNames,layerNames=layerNames)

    if nodesToIndices==False:
        indicesToNodes={}
        #for node,index in nodeNames.iteritems():
        for node in nodeNames:
            index=nodeNames[node]    
            indicesToNodes[index]=node
        nodeNames=indicesToNodes

    if layersToIndices==False:
        for aspect in range(net.aspects):
            indicesToLayers={}
            #for layer,index in layerNames[aspect].iteritems():
            for layer in layerNames[aspect]:
                index=layerNames[aspect][layer]
                indicesToLayers[index]=layer
            layerNames[aspect]=indicesToLayers

    if net.aspects==1:
        layerNames=layerNames[0]

    if nodesToIndices==None and layersToIndices==None:
        return newNet
    elif nodesToIndices!=None and layersToIndices==None:
        return newNet,nodeNames
    elif nodesToIndices==None and layersToIndices!=None:
        return newNet,layerNames
    elif nodesToIndices!=None and layersToIndices!=None:
        return newNet,nodeNames,layerNames


def threshold(net,threshold,method=">=",ignoreCouplingEdges=False):
    def accept_edge(weight,threshold,rule):
        if rule==">=":
            return weight>=threshold
        elif rule=="<=":
            return weight<=threshold
        elif rule==">":
            return weight>threshold
        elif rule=="<":
            return weight<threshold
        else:
            raise Exception("Invalid method for thresholding: "+str(rule))

    mplex=(type(net)==netmodule.MultiplexNetwork)
    if mplex:
        for coupling in net.couplings:
            if coupling[0]!="none":
                mplex=False
            

    if mplex:
        newNet=netmodule.MultiplexNetwork(couplings=net.couplings,
                                directed=net.directed,
                                noEdge=net.noEdge,
                                fullyInterconnected=net.fullyInterconnected)
    else:
        newNet=netmodule.MultilayerNetwork(aspects=net.aspects,
                                 noEdge=net.noEdge,
                                 directed=net.directed,
                                 fullyInterconnected=net.fullyInterconnected)

    #copy nodes,layers,node-layers
    for node in net:
        newNet.add_node(node)
    for aspect in range(net.aspects):
        for layer in net.slices[aspect+1]:
            newNet.add_layer(layer,aspect=aspect+1) 
    if not net.fullyInterconnected:
        for nodelayer in net.iter_node_layers():
            layer=lnodelayer[1:]
            if net.aspects==1:
                layer=layer[0]
            newNet.add_node(nodelayer[0],layer=layer)

    if mplex:
        for layer in net.iter_layers():
            for edge in net.A[layer].edges:
                if accept_edge(edge[-1],threshold,rule=method):
                    newNet.A[layer][edge[0]][edge[1]]=edge[-1]
    else:
        for edge in net.edges:
            if accept_edge(edge[-1],threshold,rule=method):
                newNet[edge[:-1]]=edge[-1]
    return newNet

def randomize_nodes_by_layer(net):
    assert isinstance(net,netmodule.MultiplexNetwork)
    assert net.aspects==1
    newnet=subnet(net,set(),net.iter_layers())
    #for layer,inet in net.A.iteritems():
    for layer in net.A:
        inet=net.A[layer]
        newinet=newnet.A[layer]
        nodes=list(inet)
        random.shuffle(nodes)
        nodemap={}
        for i,node in enumerate(inet):
            nodemap[node]=nodes[i]
            newinet.add_node(node)
        for e in inet.edges:
            newinet[nodemap[e[0]],nodemap[e[1]]]=e[2]
    return newnet



def subnet_iter(net,remove_elayers=[],remove_edges=True):
    """Iterator for all subnetworks of the given network. 

    The subnetworks need not to be induced. For multiplex networks
    the coupling edges are not removed.

    Parameters
    ----------
    net : MultilayerNetwork, or MultiplexNetwork 
       The original network.
    remove_elayers : list of ints
       List of elementary layers where removals can be done.
    remove_edges : bool
       True if edges can be removed between remaining nodes. 
       If False, then all subnetworks are induced.

    Return
    ------
    MultilayerNetwork or MultiplexNetwork objects depending on the net
    parameter.

    Examples
    --------
    Following returns all induced subnetworks when removing nodes:
    >>> subnet_iter(net,remove_elayers[0],remove_edges=False)

    Notes
    -----
    The number of subnetworks can grow very fast if the network is not very small
    or doesn't have a very small number of edges.     
    """
    #Sanity checks for parameters
    assert isinstance(net,netmodule.MultilayerNetwork), "The net parameter must be a MultilayerNetwork or MultiplexNetwork."
    assert isinstance(remove_edges,bool), "The remove_edges parameter must be True or False."
    elayersok=map(lambda a:isinstance(a,int) and 0<=a<=net.aspects,remove_elayers)
    assert all(elayersok), "The remove_elayers must be a list of ints indicating aspects of the network." 

    def all_nonzero_combinations(thelist):
        """Returns all combinations that are not empty
        """
        for i in range(1,len(thelist)+1):
            for comb in itertools.combinations(thelist,i):
                yield comb

    def all_combinations(thelist):
        """Returns all combinations
        """
        for i in range(len(thelist)+1):
            for comb in itertools.combinations(thelist,i):
                yield comb

    combinations_args=[]
    for a in range(net.aspects+1):
        if a in remove_elayers:
            combinations_args.append(all_nonzero_combinations(net.slices[a]))
        else:
            combinations_args.append([net.slices[a]])

    for nl in itertools.product(*combinations_args):
        subnet_with_edges=subnet(net,*nl)
        if remove_edges: #Going through all edge combinations
            if isinstance(net,netmodule.MultiplexNetwork):
                #For multiplex networks we do not want to go through coupling edges
                couplings=subnet_with_edges.couplings
                edges=list(subnet_with_edges.edges)
                subnet_with_edges.couplings=couplings
            else:
                #For multilayer networks we go through all edges
                edges=net.edges
            for newnet_edges in all_combinations(edges):
                newnet=subnet(subnet_with_edges,*nl,nolinks=True)
                for edge in newnet_edges:
                    newnet[edge[:-1]]=subnet_with_edges[edge[:-1]]
                yield newnet
        else: #All edges are kept
            yield subnet_with_edges
    



def get_underlying_graph(net):
    """Creates the underlying graph of a multiplex network.

    Parameters
    ----------
    net : MultilayerNetwork, or MultiplexNetwork 
       The original network.

    Return
    ------
    MultilayerNetwork objects with zero aspects.
    Node-layer tuples are converted to node names that are strings.

    Notes
    -----
    The node names are converted into strings instead of tuples because
    Python doesn't differentiate between lists of arguments and tuples
    in __getitem__ function calls.

    A useful way of extracting the tuples back from the string is to
    use the eval method.
    """

    #The network object to be returned
    newNet=netmodule.MultilayerNetwork(aspects=0,
                                       noEdge=net.noEdge,
                                       directed=net.directed
                                       )

    #Add nodes
    for nl in net.iter_node_layers():
        newNet.add_node(str(nl))

    #Add edges
    for edge in net.edges:
        n1,n2=net._link_to_nodes(edge[:-1])
        w=edge[-1]
        newNet[str(n1)][str(n2)]=w

    return newNet
