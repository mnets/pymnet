"""Data structures for handling various forms of multilayer networks.
"""

import math,itertools,pickle
import pymnet.transforms as transforms

#Pre 3.10                                                                                                                                                                                                  
try:
    from collections import MutableMapping
except ImportError:
    pass

#Post 3.10                                                                                                                                                                                                 
try:
    from collections.abc import MutableMapping
except ImportError:
    pass



COLON=slice(None,None,None)


class MultilayerNetwork(object):
    """General multilayer network with a tensor-like interface.

    See Reference [1] for background on the definition of this class.

    There are several ways of accessing the edges and nodes of the network. If there 
    is a single aspect, then the following notation can be used:

    >>> net[i,s]                   #node i at layer s
    >>> net[i,j,s,r]               #edge between nodes i and j and layers s and r
    >>> net[i,j,s] == net[i,j,s,s] #edge between nodes i and j at layer s

    Following slicing notation can also be used:

    >>> net[i,:,s,:] == net[i,s]   #node i at layer s
    >>> net[i,j,s,:]               #node i at layer s, but only links to j are visible
    >>> net[i,:,s,r]               #node i at layer s, but only links to layer r are visible
    >>> net[i,:,s] == net[i,:,s,s] 

    Similar notation holds for two (or more) aspects:

    >>> net[i,s,x]                 #node i at layer s in aspect 1 and at layer x in aspect 2
    >>> net[i,j,s,x]               #link i,j at layer s in aspect 1 and layer x in aspect 2 = i,j,s,s,x,x
    >>> net[i,j,s,r,x,y]           #link i,j between layers s and r in aspect 1 and between layers x and y in aspect 2
    >>> net[i,:,s,:,x,:] == net[i,s,x]
    >>> net[i,j,s,:,x,y]           #node i at layer s and y, but only links to j and y are visible
    >>> net[i,:,s,x] == net[i,:,s,s,x,x]


    Parameters
    ----------
    aspects : int
       Number of aspects
    noEdge : object
       Any object signifying that there is no edge.
    directed : bool
       True if the network is directed, otherwise it's
       undirected.
    fullyInterconnected : bool
       Determines if the network is fully interconnected, i.e. all nodes
       are shared between all layers. Ignored if aspects==0.

    Notes
    -----
    The default data structure behind this class is a graph similar to the 
    one described in Reference [1] implemented with nested dictionaries. 
    The downside to this implementation is that, for example, iterating through
    all the inter-layer links is not possible without inspecting also the
    inter-layer links.

    References
    ----------
    [1] Multilayer Networks. Mikko Kivela, Alexandre Arenas, Marc Barthelemy, 
    James P. Gleeson, Yamir Moreno, Mason A. Porter, arXiv:1309.7233 [physics.soc-ph]

    See also
    --------
    MultiplexNetwork : A class for multiplex networks

    """
    def __init__(self,
                 aspects=0,
                 noEdge=0,
                 directed=False,
                 fullyInterconnected=True):
        assert aspects>=0

        self.aspects=aspects
        self.directed=directed
        self.noEdge=noEdge
        self._init_slices(aspects)
        if aspects==0:
            fullyInterconnected=True
        self.fullyInterconnected=fullyInterconnected

        self._init_directions()

        #Private variables for the state of the object
        self._net={}

        if not fullyInterconnected:
            self._layerToNodes={} #key=layer,val=set of nodes
            self._nodeToLayers={} #key=node, val=set of layers

        if self.directed:
            self._rnet={} #reversed network
            self._totalDegree={}


    def _init_directions(self):
        pass

        #if self.directed:
            #self._get_degree=self._get_degree_total
            #self._get_strength=self._get_strength_total
            #self._iter_neighbors=self._iter_neighbors_total
        #else:
            #self._get_degree=self._get_degree_out
            #self._get_degree_total=self._get_degree_out
            #self._get_degree_in=self._get_degree_out
            #self._get_strength=self._get_strength_out
            #self._get_strength_total=self._get_strength_out
            #self._get_strength_in=self._get_strength_out
            #self._iter_neighbors=self._iter_neighbors_out
            #self._iter_neighbors_total=self._iter_neighbors_out
            #self._iter_neighbors_in=self._iter_neighbors_out

        #should keep table of degs and strenghts


    def _init_slices(self,aspects):
        self.slices=[] #set for each dimension
        for a in range(aspects+1):
            self.slices.append(set())
       
        
    #@classmehtod
    def _link_to_nodes(self,link):
        """Returns the link as tuple of nodes in the graph representing
        the multislice structure. I.e. when given (i,j,s_1,r_1, ... ,s_d,r_d)
        (i,s_1,...,s_d),(j,r_1,...,r_d) is returned.
        """
        return (link[0],)+link[2::2],(link[1],)+link[3::2]
    #@classmehtod
    def _nodes_to_link(self,node1,node2):
        """Returns a link when tuple of nodes is given in the graph representing
        the multislice structure. I.e. when given (i,s_1,...,s_d),(j,r_1,...,r_d) 
        (i,j,s_1,r_1, ... ,s_d,r_d) is returned.
        """
        assert len(node1)==len(node2)
        l=[]
        for i,n1 in enumerate(node1):
            l.append(n1)
            l.append(node2[i])
        return tuple(l)
    #@classmehtod
    def _short_link_to_link(self,slink):
        """ Returns a full link for the shortened version of the link. That is,
        if (i,j,s_1,...,s_d) is given as input, then (i,j,s_1,s_1,...,s_d,s_d) is 
        returned.
        """
        l=list(slink[:2])
        for k in slink[2:]:
            l.append(k)
            l.append(k)

        return tuple(l)
    
    def __len__(self):
        return len(self.slices[0])

    def __eq__(self,other):
        if not isinstance(other,MultilayerNetwork):
            return False
        
        if not self.fullyInterconnected:
            if self._nodeToLayers!=other._nodeToLayers:
                return False
        if type(self) is type(other) and self.directed == other.directed and self.directed==other.directed and self.aspects==other.aspects and self.fullyInterconnected == other.fullyInterconnected and self.noEdge == other.noEdge and self.slices==other.slices and len(self.edges) ==len(other.edges):            
            for edge in self.edges:
                if self[edge[:-1]]!=other[edge[:-1]]:
                    return False
        else:
            return False
        return True
    def __ne__(self,other):
        return not self.__eq__(other)

    def add_node(self,node,layer=None):
        """Adds an empty node to the network.

        Does nothing if node already exists. If layer is given and
        the network is not node-aligned then the node is added only
        to the given layer.

        See also
        --------
        add_layer
        """
        if isinstance(layer,list): #Lists as layers allowed
            layer=tuple(layer)

        self.slices[0].add(node)
        if layer!=None and not self.fullyInterconnected:
            #check that the layer exists, if not add it.
            if layer.__class__==tuple: #two or more aspects
                assert self.aspects>=2,layer
                for aspect_minus_one,elementary_layer in enumerate(layer):
                    if elementary_layer not in self.slices[aspect_minus_one+1]:
                        self.add_layer(elementary_layer,aspect_minus_one+1)
            else: #single aspect
                assert self.aspects==1
                if layer not in self.slices[1]:
                    self.add_layer(layer)
            self._add_node_to_layer(node,layer)

    def _add_node_to_layer(self,node,layer):
        """ Add node to layer. Network must not be node-aligned.
        """
        if node not in self._nodeToLayers:
            self._nodeToLayers[node]=set()
        self._nodeToLayers[node].add(layer)
        if layer not in self._layerToNodes:
            self._layerToNodes[layer]=set()
        self._layerToNodes[layer].add(node)


    def add_layer(self,layer,aspect=1):
        """Adds an empty layer to the network. If aspects>1, adds an elementary layer.

        Does nothing if node already exists. If aspect==0, then add_node
        is called with add_node(layer).

        See also
        --------
        add_node
        """
        if aspect==0:
            self.add_node(layer)
        else:
            self.slices[aspect].add(layer)
            #The layers are added to self._layerToNodes in a lazy way.
            #if not self.fullyInterconnected:
            #    if layer not in self._layerToNodes:
            #        self._layerToNodes[layer]=set()

    def _get_link(self,link):
        """Return link weight or 0 if no link.
        
        This is a private method, so no sanity checks on the parameters are
        done at this point.

        Parameters
        ---------
        link(tuple) : (i,j,s_1,r_1, ... ,s_d,r_d)
        """
        node1,node2=self._link_to_nodes(link)
        if node1 in self._net:
            if node2 in self._net[node1]:
                return self._net[node1][node2]
        return self.noEdge

    def _set_link(self,link,value):
        #keep track of nodes and layers in net?
        node1,node2=self._link_to_nodes(link)
        if value==self.noEdge:
            if node1 in self._net:
                if node2 in self._net[node1]:
                    if self.directed:
                        if node1==node2 and node2 in self._net[node1]:
                            self._totalDegree[node1]=self._totalDegree.get(node1,0)-1
                        else:
                            if node1 not in self._rnet or node2 not in self._rnet[node1]:
                                self._totalDegree[node1]=self._totalDegree[node1]-1
                            if node2 not in self._rnet or node1 not in self._rnet[node2]:
                                self._totalDegree[node2]=self._totalDegree[node2]-1
                        del self._rnet[node2][node1]
                    else:
                        del self._net[node2][node1]
                    del self._net[node1][node2]
        else:
            if not node1 in self._net:
                self._net[node1]={}
                if self.directed:
                    self._rnet[node1]={}
            if not node2 in self._net:
                self._net[node2]={}
                if self.directed:
                    self._rnet[node2]={}            

            if self.directed:
                if node1==node2 and node2 not in self._net[node1]:
                    self._totalDegree[node1]=self._totalDegree.get(node1,0)+1
                else:
                    if node2 not in self._net[node1] and node2 not in self._rnet[node1]:
                        self._totalDegree[node1]=self._totalDegree.get(node1,0)+1
                    if node1 not in self._net[node2] and node1 not in self._rnet[node2]:
                        self._totalDegree[node2]=self._totalDegree.get(node2,0)+1
                self._rnet[node2][node1]=value
            else:
                self._net[node2][node1]=value
            self._net[node1][node2]=value


    def _get_degree(self,node,dims=None):
        if self.directed:
            return self._get_degree_total(node,dims=dims)
        else:
            return self._get_degree_out(node,dims=dims)

    def _get_degree_in(self,node,dims=None):
        if self.directed:
            return self._get_degree_in_dir(node,dims=dims)
        else:
            return self._get_degree_out(node,dims=dims)

    def _get_degree_total(self,node,dims=None):
        if self.directed:
            return self._get_degree_total_dir(node,dims=dims)
        else:
            return self._get_degree_out(node,dims=dims)


    def _get_degree_out(self,node, dims=None):
        """Private method returning nodes degree (number of neighbors).

        See _iter_neighbors for description of the parameters.
        """
        #TODO: lookuptables for intradimensional degrees

        if dims==None:
            if node in self._net:
                return len(self._net[node])
            else:
                return 0
        else:
            return len(list(self._iter_neighbors_out(node,dims)))

    def _get_degree_total_dir(self,node,dims=None):
        """Returns the total degree of a _directed_ multilayer network.
        """
        assert self.directed
        if dims==None:
            return self._totalDegree.get(node,0)
        else:
            return len(list(self._iter_neighbors_total(node,dims)))

    def _get_degree_in_dir(self,node,dims=None):
        """Returns the in-degree of a _directed_ multilayer network.
        """
        assert self.directed
        if dims==None:
            if node in self._rnet:
                return len(self._rnet[node])
            else:
                return 0
        else:
            return len(list(self._iter_neighbors_in(node,dims)))



    def _get_strength(self,node,dims=None):
        if self.directed:
            return self._get_strength_total(node,dims=dims)
        else:
            return self._get_strength_out(node,dims=dims)
    def _get_strength_in(self,node,dims=None):
        if self.directed:
            return self._get_strength_in_dir(node,dims=dims)
        else:
            return self._get_strength_out(node,dims=dims)
    def _get_strength_total(self,node,dims=None):
        if self.directed:
            return self._get_strength_total_dir(node,dims=dims)
        else:
            return self._get_strength_out(node,dims=dims)


    def _get_strength_in_dir(self,node, dims=None):
        """Private method returning nodes in-strenght."""
        return sum(map(lambda n:self._get_link(self._nodes_to_link(n,node)),self._iter_neighbors_in(node,dims)))

    def _get_strength_out(self,node, dims=None):
        """Private method returning nodes out-strenght."""
        return sum(map(lambda n:self._get_link(self._nodes_to_link(node,n)),self._iter_neighbors_out(node,dims)))

    def _get_strength_total_dir(self,node, dims=None):
        """Private method returning nodes total strenght (sum of in- and out-strength)."""
        return self._get_strength_in(node,dims)+self._get_strength_out(node,dims)


    def _iter_neighbors(self,node,dims=None):
        if self.directed:
            return self._iter_neighbors_total(node,dims=dims)
        else:
            return self._iter_neighbors_out(node,dims=dims)
    def _iter_neighbors_in(self,node,dims=None):
        if self.directed:
            return self._iter_neighbors_in_dir(node,dims=dims)
        else:
            return self._iter_neighbors_out(node,dims=dims)
    def _iter_neighbors_total(self,node,dims=None):
        if self.directed:
            return self._iter_neighbors_total_dir(node,dims=dims)
        else:
            return self._iter_neighbors_out(node,dims=dims)

    def _iter_neighbors_out(self,node,dims=None):
        """Private method to iterate over neighbors of a node.

        Parameters
        ----------
        node(tuple) : (i,s_1,...,s_d)
        dims : If None, iterate over all neighbors. If tuple of size d+1,
               then we iterate over neighbors which are have exactly the same
               value at each dimension in the tuple or None. E.g. when
               given ('a',None,'x'), iterate over all neighbors which are node
               'a' and in slice 'x' in the second dimension.

        """
        if node in self._net:
            if dims==None:
                for neigh in self._net[node]:
                    yield neigh
            else:
                for neigh in self._net[node]:
                    if all(map(lambda i:dims[i]==None or neigh[i]==dims[i], range(len(dims)))):
                        yield neigh

    def _iter_neighbors_in_dir(self,node,dims=None):
        """Iterate over out-neighbors of a node in a directed network."""
        if node in self._rnet:
            if dims==None:
                for neigh in self._rnet[node]:
                    yield neigh
            else:
                for neigh in self._rnet[node]:
                    if all(map(lambda i:dims[i]==None or neigh[i]==dims[i], range(len(dims)))):
                        yield neigh

    def _iter_neighbors_total_dir(self,node,dims=None):
        """Iterate over in- and out-neighbors of a node in a directed network."""
        iterated=set()
        for neigh in self._iter_neighbors_out(node,dims):
            iterated.add(neigh)
            yield neigh
        for neigh in self._iter_neighbors_in(node,dims):
            if neigh not in iterated:
                yield neigh

    def __getitem__(self,item):
        """
        aspects=1
        i,s     = node i at layer s
        i,j,s   = link i,j at layer s = i,j,s,s
        i,j,s,r = link i,j between layers s and r

        i,:,s,: = i,s = node i at layer s
        i,j,s,: = node i at layer s, but only links to j are visible
        i,:,s,r = node i at layer s, but only links to layer r are visible

        i,:,s   = i,:,s,s
        Not implemented yet:
        i,s,:   = i,i,s,:

        aspects=2
        i,s,x       = node i at layer s in aspect 1 and at layer x in aspect 2
        i,j,s,x     = link i,j at layer s in aspect 1 and layer x in aspect 2 = i,j,s,s,x,x
        i,j,s,r,x,y = link i,j between layers s and r in aspect 1 and between layers x and y in aspect 2

        i,:,s,:,x,: = i,s,x
        i,j,s,:,x,y = node i at layer s and y, but only links to j and y are visible
        ...

        i,:,s,x = i,:,s,s,x,x
        Not implemented yet:
        i,s,:,x = i,i,s,:,x,x
        i,s,x,: = i,i,s,s,x,:

        i,:,s,:,x = i,:,s,:,x,x
        i,s,:,x,: = i,i,s,:,x,:
        

        """        
        d=self.aspects+1
        if not item.__class__==tuple:
            item=(item,)
        if len(item)==d: #node
            return MultilayerNode(item,self)
        elif len(item)==2*d: #link, or a node if slicing
            colons=0
            layers=[]
            for i in range(d):
                if item[2*i+1]!=COLON:
                    layers.append(item[2*i])
                else:
                    colons+=1
                    layers.append(None)
            if colons>0:
                return MultilayerNode(self._link_to_nodes(item)[0],self,layers=layers)
            else:
                return self._get_link(item)
        elif len(item)==d+1: #interslice link or node if slicing            
            if COLON not in item[2:]: #check if colons are in the slice indices
                return self[self._short_link_to_link(item)]
            else:
                raise Exception("Not implemented.")
        else:
            if d>1:
                raise KeyError("%d, %d, or %d indices please."%(d,d+1,2*d))
            else: #d==1
                raise KeyError("1 or 2 indices please.")

    def __setitem__(self,item,val):
        d=self.aspects+1

        if not item.__class__==tuple:
            item=(item,)
        if len(item)==2*d:
            link=item
            #self._set_link(item,val)
        elif len(item)==d+1:
            link=self._short_link_to_link(item)
        else:
            raise KeyError("Invalid number of indices.")

        #There might be new nodes, add them to sets of nodes
        if self.fullyInterconnected:
            for i in range(2):
                self.add_layer(link[i],int(math.floor(i/2))) #just d/2 would work, but ugly
        else:
            if self.aspects==1:
                self.add_node(link[0],layer=link[2])
                self.add_node(link[1],layer=link[3])
            else: #more than one aspect
                n1,n2=self._link_to_nodes(link)
                self.add_node(n1[0],layer=n1[1:])
                self.add_node(n2[0],layer=n2[1:])

        for i in range(2,2*d):
            self.add_layer(link[i],int(math.floor(i/2))) #just d/2 would work, but ugly


        self._set_link(link,val)



    def get_layers(self,aspect=1):
        """Returns the set of (elementary) layers (in a given aspect).
        """
        return self.slices[aspect]

    def iter_nodes(self,layer=None):
        """Iterate over nodes in the network.

        If a layer is given then returns nodes in that layer.
        """
        if self.fullyInterconnected or layer==None:
            for node in self.slices[0]:
                yield node
        else:
            if layer in self._layerToNodes:
                for node in self._layerToNodes[layer]:
                    yield node

    def __iter__(self):
        """Iterates over all nodes.
        """
        for node in self.slices[0]:
            yield node

    def iter_node_layers(self):
        """ Iterate over all node-layer pairs.
        """
        if self.fullyInterconnected:
            for nl in itertools.product(*map(lambda i:self.slices[i],range(len(self.slices)))):
                yield nl
        else:
            if self.aspects==1:
                for layer in self.iter_layers():
                    for node in self.iter_nodes(layer=layer):
                        yield (node,layer)
            else:
                for layer in self.iter_layers():
                    for node in self.iter_nodes(layer=layer):
                        yield (node,)+layer


    def iter_layers(self,aspect=None):
        """ Iterate over all layers.

        If network has multiple aspects, tuples of all layer combinations are iterated
        over. If aspect is specified and there are more than a single aspect, then elementary
        layers are iterated instead.
        """
        if aspect!=None:
            assert isinstance(aspect,int)
            assert 1<=aspect<=self.aspects
            for l in self.slices[aspect]:
                yield l
        else:
            if self.aspects>1:
                for l in itertools.product(*map(lambda i:self.slices[i],range(1,len(self.slices)))):
                    yield l
            elif self.aspects==1:
                for l in self.slices[1]:
                    yield l

    def _write_flattened(self,output):
        nodes=map(lambda x: tuple(reversed(x)),sorted(itertools.product(*map(lambda i:sorted(self.slices[i]),reversed(range(len(self.slices)))))))
        for i in nodes:
            row=[str(self[i][j]) for j in nodes]
            output.write(" ".join(row)+"\n")
        output.close()


    def __hash__(self):
        return pickle.dumps(self).__hash__()

    def get_supra_adjacency_matrix(self,includeCouplings=True):
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
        import numpy
        if self.aspects>0:
            nodes=list(map(lambda x: tuple(reversed(x)),sorted(itertools.product(*map(lambda i:sorted(self.slices[i]),reversed(range(len(self.slices))))))))
            matrix=numpy.zeros((len(nodes),len(nodes)),dtype=float)
            for i_index,i in enumerate(nodes):
                for j_index,j in enumerate(nodes):
                    if includeCouplings or i[1:]==j[1:]:
                        matrix[i_index,j_index]=self[i][j]
        else:
            nodes=sorted(self)
            matrix=numpy.zeros((len(nodes),len(nodes)),dtype=float)
            for i_index,i in enumerate(nodes):
                for j_index,j in enumerate(nodes):
                    if i_index!=j_index:
                        matrix[i_index,j_index]=self[i][j]

        return numpy.matrix(matrix),nodes

class MultilayerNode(object):
    """A node in a MultilayerNetwork. 

    The node objects are generated from the MultilayerNetwork objects with the
    __getitem__ method. The nodes can be used to access their neighboring edges,
    the neighboring edges can be iterated over by iterating the node, and the object
    contains methods for asking degree and strength of the node.
    """
    #net[1,'a','x'][:,:,'y']=net[1,:,'a',:,'x','y']
    def __init__(self,node,mnet,layers=None):
        """A node in multilayer network. 
        """
        self.node=node
        self.mnet=mnet
        self.layers=layers

    def __getitem__(self,item):
        """
        example:
        net[1,'a','x'][:,:,'y']=net[1,:,'a',:,'x','y']
        """
        if self.mnet.aspects==0:
            item=(item,)
        return self.mnet[self.mnet._nodes_to_link(self.node,item)]

    def __setitem__(self,item,value):
        if self.mnet.aspects==0:
            item=(item,)
        self.mnet[self.mnet._nodes_to_link(self.node,item)]=value

    def __len__(self):
        return self.deg()

    def deg(self,*layers):
        """Returns the degree of the node.
        """
        assert len(layers)==0 or len(layers)==(self.mnet.aspects+1)
        if layers==():
            layers=self.layers
        return self.mnet._get_degree(self.node,layers)

    def deg_total(self,*layers):
        """Returns the total degree of the node.
        """
        assert len(layers)==0 or len(layers)==(self.mnet.aspects+1)
        if layers==():
            layers=self.layers
        return self.mnet._get_degree_total(self.node,layers)

    def deg_in(self,*layers):
        """Returns the in-degree of the node.
        """
        assert len(layers)==0 or len(layers)==(self.mnet.aspects+1)
        if layers==():
            layers=self.layers
        return self.mnet._get_degree_in(self.node,layers)

    def deg_out(self,*layers):
        """Returns the out-degree of the node.
        """
        assert len(layers)==0 or len(layers)==(self.mnet.aspects+1)
        if layers==():
            layers=self.layers
        return self.mnet._get_degree_out(self.node,layers)

    def str(self,*layers):
        """Returns the weighted degree, i.e. the strength, of the node.
        """
        assert len(layers)==0 or len(layers)==(self.mnet.aspects+1)
        if layers==():
            layers=self.layers
        return self.mnet._get_strength(self.node,layers)

    def str_total(self,*layers):
        """Returns the weighted totaldegree, i.e. the strength, of the node.
        """
        assert len(layers)==0 or len(layers)==(self.mnet.aspects+1)
        if layers==():
            layers=self.layers
        return self.mnet._get_strength_total(self.node,layers)

    def str_in(self,*layers):
        """Returns the weighted in-degree, i.e. the strength, of the node.
        """
        assert len(layers)==0 or len(layers)==(self.mnet.aspects+1)
        if layers==():
            layers=self.layers
        return self.mnet._get_strength_in(self.node,layers)

    def str_out(self,*layers):
        """Returns the weighted out-degree, i.e. the strength, of the node.
        """
        assert len(layers)==0 or len(layers)==(self.mnet.aspects+1)
        if layers==():
            layers=self.layers
        return self.mnet._get_strength_out(self.node,layers)

    def __iter__(self):
        return self.iter_total()

    def layers(self,*layers):
        return MultilayerNode(self.node,self.mnet,layers=layers)

    def iter_total(self):
        for node in self._iter_nodes(self.mnet._iter_neighbors_total):
            yield node

    def iter_out(self):
        for node in self._iter_nodes(self.mnet._iter_neighbors_out):
            yield node

    def iter_in(self):
        for node in self._iter_nodes(self.mnet._iter_neighbors_in):
            yield node

    def _iter_nodes(self,iterf):
        if self.mnet.aspects>0:
            for node in iterf(self.node,self.layers):
                yield node #maybe should only return the indices that can change?
        else:
            for node in iterf(self.node,self.layers):
                yield node[0]



class MultilayerEdges:
    def __init__(self,net):
        self.net=net

    def __iter__(self):
        """Edge iterator.
        """
        if self.net.directed:
            for node in itertools.product(*self.net.slices):
                for neigh in self.net[node].iter_out():                
                    if self.net.aspects==0:
                        neigh=(neigh,)
                    link=self.net._nodes_to_link(node,neigh)
                    yield link+(self.net[link],)
        else:
            iterated=set()
            for node in itertools.product(*self.net.slices):
                for neigh in self.net[node]:                
                    if self.net.aspects==0:
                        neigh=(neigh,)
                    if neigh not in iterated:
                        link=self.net._nodes_to_link(node,neigh)
                        yield link+(self.net[link],)            
                iterated.add(node)

    def __len__(self):
        deg=0
        if self.net.directed:
            for nl in self.net.iter_node_layers():
                deg+=self.net[nl].deg_out()
            return deg
        else:
            for nl in self.net.iter_node_layers():
                deg+=self.net[nl].deg()
                if self.net[self.net._nodes_to_link(nl,nl)]!=self.net.noEdge:
                    deg+=1 #self-edges should also be counted twice
            return int(deg/2)



MultilayerNetwork.edges=property(MultilayerEdges)


class MultiplexIntraNetDict(MutableMapping):
    def __init__(self,net):
        self._net=net
        self._dict={}
    def __getitem__(self,key):
        return self._dict[key]
    def __iter__(self):
        return self._dict.__iter__()
    def __len__(self):
        return len(self._dict)
    
    def __setitem__(self,key,val):
        assert isinstance(val,MultilayerNetwork), "Invalid type of intra-layer network."
        assert val.aspects==0, "Intra-layer networks need to be monoplex networks."
        
        if key in self._dict:
            self._add_empty_network(key)
            transforms.subnet(val,val,newNet=self[key]) #copy the val to the layer
        else:
            raise Exception("No layer: "+str(key))
        
    def __delitem__(self,key):
        pass

    def _add_empty_network(self,layer):
        net=MultilayerNetworkWithParent(aspects=0,directed=self._net.directed)
        net._set_parent(self._net)
        if not self._net.fullyInterconnected:
            if self._net.aspects==1:
                net._set_name((layer,))
            else:
                net._set_name(layer)
        self._dict[layer]=net



class MultilayerNetworkWithParent(MultilayerNetwork):
    def _set_parent(self,parent):
        self.parent=parent
        if parent.fullyInterconnected:
            self.slices[0]=parent.slices[0]
    def _set_name(self,name):
        self._name=name
        if len(name)==1:
            self._layer=name[0]
        else:
            self._layer=name
    def add_node(self,node,layer=None):
        MultilayerNetwork.add_node(self,node,layer=layer)
        if self.parent.fullyInterconnected:
            self.parent.add_node(node)
        else:
            self.parent.add_node(node,layer=self._layer)            

        if not self.parent.fullyInterconnected:
            if node not in self.parent._nodeToLayers:
                 self.parent._nodeToLayers[node]=set()
            self.parent._nodeToLayers[node].add(self._layer)


class MultiplexNetwork(MultilayerNetwork):
    """Multiplex network as a special case of multilayer network.

    Parameters
    ----------
    couplings : list, str, tuple, None, MultilayerNetwork
       Parameter determining how the layers are coupled, i.e. what 
       inter-layer edges are present.
       If string, the parameter must be on of the  policy types: 
       'ordinal', 'categorical', or 'none'. None is same as 'none'. Tuple
       can be used to give parameters to the coupling types, e.g. 
       ('categorical',1.0) is categorical coupling with inter-edge weights
       equal to 1.0. If coupling is a network, it must be a monoplex one
       with the nodes corresponding to layer names. If a list is given, then
       the multiplex network will have aspects equal to the length of that
       list with each element corresponding to a coupling given as described
       above.
    noEdge : object
       Any object signifying that there is no edge.
    directed : bool
       True if the network is directed, otherwise it's
       undirected.
    fullyInterconnected : bool
       Determines if the network is fully interconnected, i.e. all nodes
       are shared between all layers.
    
    Notes
    -----
    The default implementation for this type of networks is 'sequence of
    graphs'. That is, each intra-layer network is stored separately and 
    accessing and modifying the intra-layer networks is independent of the
    other intra-layer networks. The couplings edges are not stored explicitly
    but they are only generated when needed.

    See also
    --------
    MultilayerNetwork : A class for more general type of multilayer networks

    """


    def __init__(self,couplings=None,directed=False,noEdge=0,fullyInterconnected=True):
        self.directed=directed
        self.noEdge=noEdge

        self.fullyInterconnected=fullyInterconnected
        if not fullyInterconnected:
            self._nodeToLayers={}

        coupling_types=["categorical","ordinal","none"]
        self.couplings=[]

        if isinstance(couplings,tuple) or isinstance(couplings,"".__class__) or isinstance(couplings,u"".__class__) or isinstance(couplings,MultilayerNetwork) or couplings==None:
            couplings=[couplings]

        if isinstance(couplings,list):
            for coupling in couplings:
                if isinstance(coupling,tuple):
                    assert len(coupling)!=0
                    assert coupling[0] in coupling_types
                    if coupling[0] in ["categorical","ordinal"] and len(coupling)==1:
                        coupling=coupling+(1.0,)
                    self.couplings.append(coupling)
                elif isinstance(coupling,MultilayerNetwork):
                    assert coupling.aspects==0
                    self.couplings.append((coupling,))
                elif isinstance(coupling,"".__class__) or isinstance(coupling,u"".__class__):
                    assert str(coupling) in coupling_types
                    self.couplings.append((coupling,1.0))
                elif coupling==None:
                    self.couplings.append(("none",))
                else:
                    raise ValueError("Invalid coupling type: "+str(type(coupling)))
            self.aspects=len(couplings)
        else:
            raise ValueError("Invalid coupling type: "+str(type(couplings)))

        self._init_slices(self.aspects)
        
        #diagonal elements, map with keys as tuples of slices and vals as MultiSliceNetwork objects
        #keys are not tuples if dimensions==2
        self.intranets=MultiplexIntraNetDict(self)
        self.A=self.intranets

        self._init_directions()

    def _get_edge_inter_aspects(self,link):
        r"""Returns list of aspects where the two nodes of $G_M$ differ.
        """
        dims=[]
        for d in range(self.aspects+1):
            if link[2*d]!=link[2*d+1]:
                dims.append(d)
        return dims

    def _get_A_with_tuple(self,layer):
        """Return self.A. Layer must be given as tuple.
        """
        if self.aspects==1:
            return self.A[layer[0]]
        else:
            return self.A[layer]

    def add_layer(self,layer,aspect=1):
        """ Adds node or a layer to given aspect in the network.

        Examples
        --------
        >>> myNet.add_layer('myLayer',1) #Adds a new layer to the first aspect
        """
        #overrrides the parent method

        #check if new diagonal matrices needs to be added
        if layer not in self.slices[aspect]:
            if aspect>0:            
                if self.aspects>1:
                    new_slices=list(self.slices[1:])
                    new_slices[aspect-1]=[layer]
                    for s in itertools.product(*new_slices):
                        self.A._add_empty_network(s)
                else:
                    self.A._add_empty_network(layer)

            if aspect==0:
                self.add_node(layer)
            else:
                self.slices[aspect].add(layer)
            #call parent method
            #MultilayerNetwork.add_layer(self,layer,aspect)


    def _has_layer_with_tuple(self,layer):
        """Return true if layer in self.A. Layer must be given as tuple.
        """
        if self.aspects==1:
            return layer[0] in self.A
        else:
            return layer in self.A


    def _get_link(self,link):
        """Overrides parents method.
        """
        d=self._get_edge_inter_aspects(link)
        if len(d)==1: #not a self-link, or link with multiple different cross-aspects
            if d[0]>0:
                assert link[0]==link[1]
                if not link[0] in self.slices[0]:
                    return self.noEdge
                if not self.fullyInterconnected:
                    supernode1, supernode2=self._link_to_nodes(link)
                    if not (link[0] in self._get_A_with_tuple(supernode1[1:]).slices[0] and link[0] in self._get_A_with_tuple(supernode2[1:]).slices[0]):
                        return self.noEdge
                coupling=self.couplings[d[0]-1]                
                if coupling[0]=="categorical":
                        return coupling[1] 
                elif coupling[0]=="ordinal":
                    if link[2*d[0]]+1==link[2*d[0]+1] or link[2*d[0]]==link[2*d[0]+1]+1:
                        return coupling[1]
                    else:
                        return self.noEdge
                elif isinstance(coupling[0],MultilayerNetwork):
                    return self.couplings[d[0]-1][0][link[2*d[0]],link[2*d[0]+1]]
                else:
                    raise Exception("Coupling not implemented: "+str(coupling))
            else:
                if self._has_layer_with_tuple(link[2::2]):
                    return self._get_A_with_tuple(link[2::2])[link[0],link[1]]
                else:
                    return self.noEdge
        else:
            return self.noEdge
                
    def _set_link(self,link,value):
        """Overrides parents method.
        """
        d=self._get_edge_inter_aspects(link)
        if len(d)==1 and d[0]==0:
            S=link[2::2]
            self._get_A_with_tuple(S)[link[0],link[1]]=value
        elif len(d)==0:
            raise KeyError("No self-links.")
        else:
            raise KeyError("Can only set links in the node dimension.")


    def _get_dim_degree(self,supernode,aspect,direction="tot"):
        coupling_type=self.couplings[aspect-1][0]
        if coupling_type=="categorical":
            if self.fullyInterconnected:
                return len(self.slices[aspect])-1
            else:
                if self.aspects>1:
                    layer=supernode[1:]
                else:
                    layer=supernode[1]
                if layer in self._nodeToLayers[supernode[0]]:
                    if self.aspects==1:
                        return len(self._nodeToLayers[supernode[0]])-1
                    else:
                        return len(filter(lambda x:x[aspect]==supernode[aspect],self._nodeToLayers[supernode[0]])) -1
                else:
                    return 0
        elif coupling_type=="ordinal":
            up,down=supernode[aspect]+1,supernode[aspect]-1
            if self.fullyInterconnected:
                return int(up in self.slices[aspect])+int(down in self.slices[aspect])
            else:
                return int(supernode[:aspect]+(up,)+supernode[aspect+1:] in self._nodeToLayers[supernode[0]])+int(supernode[:aspect]+(down,)+supernode[aspect+1:] in self._nodeToLayers[supernode[0]])
        elif isinstance(coupling_type,MultilayerNetwork):
            if direction=="tot":
                return self.couplings[aspect-1][0][supernode[aspect]].deg_total()
            elif direction=="in":
                return self.couplings[aspect-1][0][supernode[aspect]].deg_in()
            elif direction=="out":
                return self.couplings[aspect-1][0][supernode[aspect]].deg_out()
        elif coupling_type=="none":
            return 0
        else:
            raise Exception("Coupling '"+str(coupling_type)+"' not implemented.")

    def _get_dim_strength(self,node,aspect,direction="tot"):
        coupling_str=self.couplings[aspect-1][1]
        coupling_type=self.couplings[aspect-1][0]
        if isinstance(coupling_type,MultilayerNetwork):
            raise Exception() #please implement this
        return self._get_dim_degree(node,aspect,direction=direction)*coupling_str


    def _iter_dim(self,supernode,aspect,direction="tot"):
        coupling_type=self.couplings[aspect-1][0]
        if coupling_type=="categorical":            
            if self.fullyInterconnected:
                for n in self.slices[aspect]:
                    if n!=supernode[aspect]:                    
                        yield supernode[:aspect]+(n,)+supernode[aspect+1:]
            elif supernode[0] in self._get_A_with_tuple(supernode[1:]).slices[0]:
                for layers in self._nodeToLayers[supernode[0]]:
                    if self.aspects>1:
                        if layers!=supernode[1:]:
                            yield (supernode[0],)+layers
                    else:
                        if layers!=supernode[1]:
                            yield (supernode[0],layers)
        elif coupling_type=="ordinal":
            up,down=supernode[aspect]+1,supernode[aspect]-1
            if self.fullyInterconnected:
                if up in self.slices[aspect]:
                    yield supernode[:aspect]+(up,)+supernode[aspect+1:]
                if down in self.slices[aspect]:
                    yield supernode[:aspect]+(down,)+supernode[aspect+1:]
            else:
                if supernode[1:aspect]+(up,)+supernode[aspect+1:] in self._nodeToLayers[supernode[0]]:
                    yield supernode[:aspect]+(up,)+supernode[aspect+1:]
                if supernode[1:aspect]+(down,)+supernode[aspect+1:] in self._nodeToLayers[supernode[0]]:
                    yield supernode[:aspect]+(down,)+supernode[aspect+1:]
        elif coupling_type=="none":
            pass
        else:
            raise NotImplemented()
        
    def _select_dimensions(self,node,dims):
        if dims==None:
            for d in range(self.aspects+1):
                yield d
        else:
            l=[]
            for d,val in enumerate(dims):
                if val!=None and node[d]!=val:
                    return
                if val==None:
                    l.append(d)
            for d in l:
                yield d

    def _get_degree_total_dir(self,node, dims):
        """Overrides parents method.
        """
        k=0
        for d in self._select_dimensions(node,dims):
            if d==0:
                k+=self._get_A_with_tuple(node[1:])[node[0]].deg_total()
            else:
                k+=self._get_dim_degree(node,d,direction="tot")
        return k

    def _get_degree_in_dir(self,node, dims):
        """Overrides parents method.
        """
        k=0
        for d in self._select_dimensions(node,dims):
            if d==0:
                k+=self._get_A_with_tuple(node[1:])[node[0]].deg_in()
            else:
                k+=self._get_dim_degree(node,d,direction="in")
        return k

    def _get_degree_out(self,node, dims):
        """Overrides parents method.
        """
        k=0
        for d in self._select_dimensions(node,dims):
            if d==0:
                k+=self._get_A_with_tuple(node[1:])[node[0]].deg_out()
            else:
                k+=self._get_dim_degree(node,d,direction="out")
        return k


    def _get_strength_total_dir(self,node, dims):
        """Overrides parents method.
        """
        s=0
        for d in self._select_dimensions(node,dims):
            if d==0:
                s+=self._get_A_with_tuple(node[1:])[node[0]].str_total()
            else:
                s+=self._get_dim_strength(node,d,direction="tot")
        return s


    def _get_strength_in_dir(self,node, dims):
        """Overrides parents method.
        """
        s=0
        for d in self._select_dimensions(node,dims):
            if d==0:
                s+=self._get_A_with_tuple(node[1:])[node[0]].str_in()
            else:
                s+=self._get_dim_strength(node,d,direction="in")
        return s


    def _get_strength_out(self,node, dims):
        """Overrides parents method.
        """
        s=0
        for d in self._select_dimensions(node,dims):
            if d==0:
                s+=self._get_A_with_tuple(node[1:])[node[0]].str_out()
            else:
                s+=self._get_dim_strength(node,d,direction="out")
        return s



    def _iter_neighbors_total_dir(self,node,dims):
        """Overrides parents method.
        """
        for d in self._select_dimensions(node,dims):
            if d==0:                
                for n in self._get_A_with_tuple(node[1:])._iter_neighbors_total((node[0],)):
                    yield (n[0],)+node[1:]
            else:
                for n in self._iter_dim(node,d,direction="tot"):
                    yield n

    def _iter_neighbors_in_dir(self,node,dims):
        """Overrides parents method.
        """
        for d in self._select_dimensions(node,dims):
            if d==0:                
                for n in self._get_A_with_tuple(node[1:])._iter_neighbors_in((node[0],)):
                    yield (n[0],)+node[1:]
            else:
                for n in self._iter_dim(node,d,direction="in"):
                    yield n

    def _iter_neighbors_out(self,node,dims):
        """Overrides parents method.
        """
        for d in self._select_dimensions(node,dims):
            if d==0:                
                for n in self._get_A_with_tuple(node[1:])._iter_neighbors_out((node[0],)):
                    yield (n[0],)+node[1:]
            else:
                for n in self._iter_dim(node,d,direction="out"):
                    yield n

    def __eq__(self,other):
        if type(self) is type(other):
            if self.directed == other.directed and self.directed==other.directed and self.aspects==other.aspects and self.fullyInterconnected == other.fullyInterconnected and self.noEdge == other.noEdge and self.slices==other.slices and self.couplings == other.couplings:
                for layer in self.iter_layers():
                    if self.A[layer]!=other.A[layer]:
                        return False
                return True
        return False

    def iter_nodes(self,layer=None):
        """Iterate over nodes in the network.

        If a layer is given then returns nodes in that layer.
        """
        if self.fullyInterconnected or layer==None:
            for node in self.slices[0]:
                yield node
        else:
            for node in self.A[layer]:
                yield node

    def _add_node_to_layer(self,node,layer):
        """ Add node to layer. Network must not be node-aligned and the layer
        must exist.
        """
        if node not in self._nodeToLayers:
            self._nodeToLayers[node]=set()
        self._nodeToLayers[node].add(layer)
        if node not in self.A[layer]:
            self.A[layer].add_node(node)

class FlatMultilayerNetworkView(MultilayerNetwork):
    """

    fnet[(1,'a','b')]
    fnet[(1,'a','b'),(2,'a','b')]

    """
    def __init__(self,mnet):
        self.mnet=mnet
        self.aspects=0

    def _flat_node_to_node(self,node):
        pass

    def _flat_edge_to_edge(self,edge):
        pass


    def _get_link(self,link):
        """Overrides parents method.
        """
        return self.mnet[tuple(itertools.chain(*zip(*a)))]
                
    def _set_link(self,link,value):
        """Overrides parents method.
        """
        raise NotImplemented("yet.")

    def _get_degree(self,node, dims):
        """Overrides parents method.
        """
        raise NotImplemented("yet.")

    def _iter_neighbors(self,node,dims):
        """Overrides parents method.
        """
        raise NotImplemented("yet.")

class ModularityMultilayerNetworkView(MultilayerNetwork):
    def __init__(self,mnet,gamma=1.0):
        self.gamma=gamma
        self.mnet=mnet

        self.slices=mnet.slices
        self.aspects=mnet.aspects

        #precalc ms,u
        self.m={}
        for s in itertools.product(*mnet.slices[1:]):
            for node in mnet:
                self.m[s]=self.m.get(s,0)+mnet[(node,)+s][(COLON,)+s].str()
            self.m[s]=self.m[s]/2.0
        self.u=0
        for i in itertools.product(*mnet.slices):
            for j in itertools.product(*mnet.slices):
                self.u+=mnet[i][j]
        self.oneper2u=1.0/self.u/2.0

    def _get_link(self,item):
        v=self.mnet[item]

        if item[2::2]==item[3::2]: #its inside slice
            s=item[2::2]
            kis=self.mnet[(item[0],)+s][(COLON,)+s].str()
            kjs=self.mnet[(item[1],)+s][(COLON,)+s].str()
            ms=self.m[s]
            return v-self.gamma*kis*kjs/float(2.0*ms)
        else:
            return v


try:
    import networkx
    class FlattenedMultilayerNetworkxView(networkx.Graph):
        pass
except ImportError:
    pass



if __name__ == '__main__':
    import tests.net_test
    tests.net_test.test_net()
