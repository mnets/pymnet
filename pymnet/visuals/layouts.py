"""Module for creating network layouts.
"""

import pymnet
import math,random

def get_layout(layout,net,alignedNodes=True,**kwargs):
    """Function for calculating a layout for a network. For parameter values see documentation
    of the draw function.

    Returns
    -------
    nodeCoords, nodelayerCoords : dict, dict
       Node coordinates and node-layer coordinates that are generated. These can be given to the
       draw function as parameters.
    """
    if alignedNodes==None:
         if isinstance(net,pymnet.net.MultiplexNetwork):
              alignedNodes=True
         elif isinstance(net,pymnet.net.MultilayerNetwork):
              alignedNodes=False
         else:
              raise ValueError("The argument net must be a MultilayerNetwork or Multiplex network.")

    ncoords,nlcoords={},{}
    if alignedNodes:
        if layout in ["circular","shell","spring","spectral"]: #nx layout
            if hasattr(pymnet,"nx"):
                la=getattr(pymnet.nx,layout+"_layout")
                na=pymnet.transforms.aggregate(net,1)
                ncoords=la(na,**kwargs)
            else:
                raise Exception("Networkx needs to be installed to use layout: "+layout)
        elif layout=="random":
            for node in net:
                ncoords[node]=(random.random(),random.random())
        elif layout=="fr":
            ncoords=get_fruchterman_reingold_multilayer_layout(net)
        else:
            raise Exception("Invalid layout: "+layout)
    else:
        if layout=="random":
            for nl in net.iter_node_layers():
                nlcoords[nl]=(random.random(),random.random())
        elif layout=="fr":
            nlcoords=get_fruchterman_reingold_multilayer_layout(net)
        else:
            raise Exception("Invalid layout: "+layout)
    return ncoords,nlcoords         




def normalize_coordinates(coords,boxSize,inplace=False):
    """Normalizes coordinates (linearly) such that coordinate min is zero and max is 
    the one given by the boxSize.

    Parameters
    ----------
    coords : dict
       Dictionary of coordinates, where keys are nodes/node-layers and values are tuples
       in the format (x,y)
    boxSize : tuple of floats
       The size of the box where the coordinates are to be normalized
    """
    minx,miny,maxx,maxy=None,None,None,None
    #for node,(x,y) in coords.iteritems():
    for node in coords:
        x,y=coords[node]
        if minx==None or x<minx:
            minx=x
        if miny==None or y<miny:
            miny=y
        if maxx==None or x>maxx:
            maxx=x
        if maxy==None or y>maxy:
            maxy=y

    difx=maxx-minx
    dify=maxy-miny
    if inplace:
        newcoords=coords
    else:
        newcoords={}
    #for node, (x, y) in coords.iteritems():
    for node in coords:
        x,y=coords[node]
        newcoords[node]=((x-minx)/difx, (y-miny)/dify )
    return newcoords 


def get_fruchterman_reingold_multilayer_layout(net,
                                               nodeDist="auto",
                                               boxSize=1.0,
                                               alignedNodes=True,
                                               nodelayerCoords=None,
                                               nodeCoords=None,
                                               fixedNodes=None,
                                               fixedNodeLayers=None,
                                               iterations=100):
    """A multilayer version of the Fructherman-Reingold algorithm for network layouts.

    This is a mulitlayer variation of the standard FR algorithm, where the layout is 
    produced by simulating springs between linked nodes and repulsive forces between all 
    nodes. The main difference to the normal version of the algorithm is that the nodes 
    which are on different layers do not repulse each other.

    Parameters
    ----------
    net : MultilayerNetwork
       The network for which the coordinates are calculated
    nodeDist : float, string
       The desired distance between pairs of nodes. If "auto", then inverse of the 
       square root of the number of nodes is used.
    boxSize : float, tuple of floats
       The size of the bounding box for the coordinates. If float is given then a square
       box is used. Otherwise, provide a tuple with two floats.
    alignedNodes : bool
       Determines if the nodes-layer tuples with the same node should have the same 
       coordinates. 
    nodelayerCoords : dict, None
       Initial coordinates for node-layer tuples. If None, random coordinates are used.
       If alignedNodes is set to True these coordinates are not used.
    nodeCoords : dict, None    
       Initial coordinates for nodes. If None, random coordinates are used. If a coordinate
       for node-layer tuple is defined then that is used instead of the node coordinate.
    fixedNodes : set, None
       The set of nodes that are not moved from the initial coordinates. If None, then 
       all nodes are allowed to move. You can also use list or similar data structures, but
       set is recommended for speed when the number of elements is large.
    fixedNodeLayers : set, None
       The set of nodes-layers that are not moved from the initial coordinates. If None, then 
       all node-layers are allowed to move. You can also use list or similar data structures, but
       set is recommended for speed when the number of elements is large.
    iterations : int
       The number of times the nodes/node-layer tuples are moved.
    """

    #Parsing parameters and sanity check for them
    #net
    assert isinstance(net,pymnet.MultilayerNetwork), "Invalid network type"
    assert net.aspects>=1, "No monoplex networks"

    #If the network is fully interconnected, we just create network with one layer
    if net.fullyInterconnected:
        assert nodelayerCoords==None, "Only node coordinates for fully interconnected networks"
        magg=pymnet.MultiplexNetwork(fullyInterconnected=False)
        magg.add_layer("all")
        magg.A["all"]=pymnet.transforms.aggregate(net,1)
        net=magg

    #nodeDist
    if nodeDist=="auto":
        nodeDist=1./math.sqrt(len(net.slices[0]))
    else:
        nodeDist=float(nodeDist)
        assert nodeDist>0
    
    #boxSize
    if isinstance(boxSize, tuple) or isinstance(boxSize, list):
        assert len(boxSize)==2
    else:
        boxSize=float(boxSize)
        boxSize=(boxSize,boxSize)

    #nodeCoords
    if nodeCoords==None:
        nodeCoords={}

    #nodelayerCoords
    if nodelayerCoords==None:
        nodelayerCoords={}

    if alignedNodes: #use node coordinates
        nc={}
        for node in net:
            if node in nodeCoords:
                nc[node]=nodeCoords[node]
            else:
                nc[node]=(boxSize[0]*random.random(), boxSize[1]*random.random())
    else: #use node-layer tuple coordinates
        nlc={}
        for nl in net.iter_node_layers():
            if nl in nodelayerCoords:
                nlc[nl]=nodelayerCoords[nl]
            elif nl[0] in nodeCoords:
                nlc[nl]=nodeCoords[nl[0]]
            else:
                nlc[nl]=(boxSize[0]*random.random(), boxSize[1]*random.random())

    if fixedNodes==None:
        fixedNodes=set()
    if fixedNodeLayers==None:
        fixedNodeLayers=set()            

    #Parsing complete

    #Some internal parameters
    temperature=0.1*max(boxSize)
    delta_temperature=temperature/float(iterations)
    min_dist=0.01

    for iteration in range(iterations):        
        if alignedNodes: #we have coordinates for nodes
            delta_nc=dict( ( (k,(0.,0.)) for k in nc ) )
            #Spring forces
            for edge in net.edges:
                node1=edge[0]
                node2=edge[1]
                if node1!=node2:
                    diff=(nc[node1][0]-nc[node2][0], nc[node1][1]-nc[node2][1])
                    dist=math.sqrt(diff[0]**2+diff[1]**2)
                    c=dist/float(nodeDist)
                    delta_nc[node1]=(delta_nc[node1][0]-c*diff[0],delta_nc[node1][1]-c*diff[1])
                    delta_nc[node2]=(delta_nc[node2][0]+c*diff[0],delta_nc[node2][1]+c*diff[1])
            
            #Repulsive forces
            for node1 in net:
                for node2 in net:
                    if node1!=node2:
                        layer_overlap=len(net._nodeToLayers[node1].intersection(net._nodeToLayers[node2]))
                        diff=(nc[node1][0]-nc[node2][0], nc[node1][1]-nc[node2][1])
                        dist=math.sqrt(diff[0]**2+diff[1]**2)
                        dist=max(dist,min_dist)
                        c=layer_overlap*nodeDist**2/float(dist**2)
                        delta_nc[node1]=(delta_nc[node1][0]+c*diff[0],delta_nc[node1][1]+c*diff[1])
                        delta_nc[node2]=(delta_nc[node2][0]-c*diff[0],delta_nc[node2][1]-c*diff[1])
                    
            #Normalize coordinate, and apply them
            #for node,(x,y) in delta_nc.iteritems():
            for node in delta_nc:
                x,y=delta_nc[node]
                if node not in fixedNodes:
                    delta_len=math.sqrt(x**2+y**2)
                    nc[node]=(nc[node][0]+temperature*delta_len*x, nc[node][1]+temperature*delta_len*y)
            normalize_coordinates(nc,boxSize,inplace=True)

        else: #we have coordinates for node-layer tuples
            
            #There is currently a lot of code dublication here when compared to the 
            #case where nodes are aligned. Some of this should be removed, and some
            #of it will probably disappear once the code is optimized a bit.

            delta_nlc=dict( ( (k,(0.,0.)) for k in nlc ) )
            #Spring forces
            for edge in net.edges:
                nl1,nl2=net._link_to_nodes(edge[:-1])
                diff=(nlc[nl1][0]-nlc[nl2][0], nlc[nl1][1]-nlc[nl2][1])
                dist=math.sqrt(diff[0]**2+diff[1]**2)
                dist=max(dist,min_dist)
                c=dist/float(nodeDist)
                delta_nlc[nl1]=(delta_nlc[nl1][0]-c*diff[0],delta_nlc[nl1][1]-c*diff[1])
                delta_nlc[nl2]=(delta_nlc[nl2][0]+c*diff[0],delta_nlc[nl2][1]+c*diff[1])
                        
            #Repulsive forces
            for nl1 in net.iter_node_layers():
                layer=nl1[1:][0] if net.aspects==1 else nl1[1:]
                for node2 in net.iter_nodes(layer=layer):
                    nl2=(node2,)+nl1[1:]
                    if nl1!=nl2:
                        diff=(nlc[nl1][0]-nlc[nl2][0], nlc[nl1][1]-nlc[nl2][1])
                        dist=math.sqrt(diff[0]**2+diff[1]**2)
                        dist=max(dist,min_dist)
                        c=nodeDist**2/float(dist**2)
                        delta_nlc[nl1]=(delta_nlc[nl1][0]+c*diff[0],delta_nlc[nl1][1]+c*diff[1])
                        delta_nlc[nl2]=(delta_nlc[nl2][0]-c*diff[0],delta_nlc[nl2][1]-c*diff[1])
                    
            #Normalize coordinate, and apply them
            #for nl,(x,y) in delta_nlc.iteritems():
            for nl in delta_nlc:
                x,y=delta_nlc[nl]
                if nl not in fixedNodeLayers:
                    delta_len=math.sqrt(x**2+y**2)
                    nlc[nl]=(nlc[nl][0]+temperature*delta_len*x, nlc[nl][1]+temperature*delta_len*y)
            normalize_coordinates(nlc,boxSize,inplace=True)

        temperature-=delta_temperature
    

    if alignedNodes:
        return nc
    else:
        return nlc