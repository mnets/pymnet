import networkx,math,itertools

COLON=slice(None,None,None)


class SparseTensor(object):
    def __init__(self,dimensions):
        self.dimensions=dimensions
        self.items={}
    def __getitem__(self,*item):
        assert len(item)==self.dimensions
        return self.items.get(item,0)
    def __setitem__(self,item,value):
        assert len(item)==self.dimensions
        self.items[item]=value

class MultisliceNetwork(object):
    """Multislice network with arbitrary number of dimension and a tensor-like interface.

    """
    def __init__(self,
                 dimensions=1,
                 noEdge=0,
                 directed=False):
        assert dimensions>=0

        self.dimensions=dimensions
        self.directed=directed
        self.noEdge=noEdge
        self._init_slices(dimensions)
        

        if directed:
            self.net=networkx.DiGraph()
        else:
            self.net=networkx.Graph()        

        #should keep table of degs and strenghts

    def _init_slices(self,dimensions):
        self.slices=[] #set for each dimension
        for d in range(dimensions):
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

    def add_node(self,node,dimension):
        """Adds an empty node to the dimension.
        Does nothing if node already exists.
        """
        self.slices[dimension].add(node)

    def _get_link(self,link):
        """Return link weight or 0 if no link.
        
        This is a private method, so no sanity checks on the parameters are
        done at this point.

        Paramters
        ---------
        link(tuple) : (i,j,s_1,r_1, ... ,s_d,r_d)
        """
        node1,node2=self._link_to_nodes(link)
        if node1 in self.net:
            if node2 in self.net[node1]:
                return self.net[node1][node2]['weight']
        return self.noEdge

    def _set_link(self,link,value):        
        node1,node2=self._link_to_nodes(link)
        if value==self.noEdge:
            if node1 in self.net:
                if node2 in self.net[node1]:
                    self.net.remove_edge(node1,node2)
        else:
            self.net.add_edge(node1,node2,weight=value)

    def _get_degree(self,node, dims=None):
        """Private method returning nodes degree (number of neighbors).

        See _iter_neighbors for description of the parameters.
        """
        #TODO: lookuptables for intradimensional degrees

        if dims==None:
            return self.net.degree(node)
        else:
            return len(list(self._iter_neighbors(node,dims)))

    def _get_strength(self,node, dims=None):
        """Private method returning nodes strenght (sum of weights).

        See _iter_neighbors for description of the parameters.
        """
        #TODO: lookuptables for intradimensional strengths        
        return sum(map(lambda n:self._get_link(self._nodes_to_link(node,n)),self._iter_neighbors(node,dims)))


    def _iter_neighbors(self,node,dims):
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
        if node in self.net:
            if dims==None:
                for neigh in self.net[node]:
                    yield neigh
            else:
                for neigh in self.net[node]:
                    if all(map(lambda i:dims[i]==None or neigh[i]==dims[i], range(len(dims)))):
                        yield neigh

    def __getitem__(self,item):
        """
        dimensions=2
        i,s     = node i at slice s
        i,j,s   = link i,j at slice s = i,j,s,s
        i,j,s,r = link i,j between slices s and r

        i,:,s,: = i,s = node i at slice s
        i,j,s,: = node i at slice s, but only links to j are visible
        i,:,s,r = node i at slice s, but only links to slide r are visible

        i,:,s   = i,:,s,s
        Not implemented yet:
        i,s,:   = i,i,s,:

        dimensions=3
        i,s,x       = node i at slice s in dimension 1 and at slice x in dimension 2
        i,j,s,x     = link i,j at slice s in dim 1 and slice x in dim 2 = i,j,s,s,x,x
        i,j,s,r,x,y = link i,j between slices s and r in dim 1 and between slices x and y in dim 2

        i,:,s,:,x,: = i,s,x
        i,j,s,:,x,y = node i at slice s and y, but only links to j and y are visible
        ...

        i,:,s,x = i,:,s,s,x,x
        Not implemented yet:
        i,s,:,x = i,i,s,:,x,x
        i,s,x,: = i,i,s,s,x,:

        i,:,s,:,x = i,:,s,:,x,x
        i,s,:,x,: = i,i,s,:,x,:
        

        """        
        d=self.dimensions
        if not isinstance(item,tuple):
            item=(item,)
        if len(item)==d: #node
            return MultisliceNode(item,self)
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
                return MultisliceNode(self._link_to_nodes(item)[0],self,layers=layers)
            else:
                return self._get_link(item)
        elif len(item)==d+1: #interslice link or node if slicing            
            if COLON not in item[2:]: #check if colons are in the slice indices
                return self[self._short_link_to_link(item)]
            else:
                raise NotImplemented("yet.")
        else:
            if d>1:
                raise KeyError("%d, %d, or %d indices please."%(d,d+1,2*d))
            else: #d==1
                raise KeyError("1 or 2 indices please.")

    def __setitem__(self,item,val):
        d=self.dimensions

        if not isinstance(item,tuple):
            item=(item,)
        if len(item)==2*d:
            link=item
            self._set_link(item,val)
        elif len(item)==d+1:
            link=self._short_link_to_link(item)
        else:
            raise KeyError("Invalid number of indices.")

        #There might be new nodes, add them to sets of nodes
        for i in range(2*d):
            self.add_node(link[i],int(math.floor(i/2))) #just d/2 would work, but ugly

        self._set_link(link,val)



    def iter_dimension(self,dimension):
        for node in self.slices[dimension]:
            yield node

    def __iter__(self):
        """Iterates over all nodes.
        """
        for node in self.slices[0]:
            yield node

    @property
    def edges(self):
        if self.directed:
            for node in itertools.product(*self.slices):
                for neigh in self[node]:                
                    if self.dimensions==1:
                        neigh=(neigh,)
                    link=self._nodes_to_link(node,neigh)
                    yield link+(self[link],)
        else:
            iterated=set()
            for node in itertools.product(*self.slices):
                for neigh in self[node]:                
                    if self.dimensions==1:
                        neigh=(neigh,)
                    if neigh not in iterated:
                        link=self._nodes_to_link(node,neigh)
                        yield link+(self[link],)            
                iterated.add(node)

    def deg(self,*args):
        """
        net.deg(i)
        net.deg(i,s,x)
        net.deg(i,s)==net.deg(i,s,:)
        net.deg(i,None,x)
        """
        pass

    def str(self,*args):
        """Strenght, see deg.
        """
        pass

    def write_flattened(self,output):
        nodes=map(lambda x: tuple(reversed(x)),sorted(itertools.product(*map(lambda i:sorted(self.slices[i]),reversed(range(len(self.slices)))))))
        for i in nodes:
            row=[str(self[i][j]) for j in nodes]
            output.write(" ".join(row)+"\n")
        #print " ".join(row)
        output.close()


    def get_supra_adjacency_matrix(self):
        import numpy
        nodes=map(lambda x: tuple(reversed(x)),sorted(itertools.product(*map(lambda i:sorted(self.slices[i]),reversed(range(len(self.slices)))))))
        matrix=numpy.zeros((len(nodes),len(nodes)),dtype=int)
        for i_index,i in enumerate(nodes):
            for j_index,j in enumerate(nodes):
                matrix[i_index,j_index]=self[i][j]
        return numpy.matrix(matrix),nodes

class MultisliceNode(object):
    def __init__(self,node,mnet,layers=None):
        """A node in multilice network. 

        ...
        """
        self.node=node
        self.mnet=mnet
        self.layers=layers

    def __getitem__(self,item):
        """
        example:
        net[1,'a','x'][:,:,'y']=net[1,:,'a',:,'x','y']
        """
        if self.mnet.dimensions==1:
            item=(item,)
        return self.mnet[self.mnet._nodes_to_link(self.node,item)]

    def __setitem__(self,item,value):
        if self.mnet.dimensions==1:
            item=(item,)
        self.mnet[self.mnet._nodes_to_link(self.node,item)]=value

    def deg(self,*layers):
        assert len(layers)==0 or len(layers)==self.mnet.dimensions
        if layers==():
            layers=self.layers
        return self.mnet._get_degree(self.node,layers)
    def str(self,*layers):
        assert len(layers)==0 or len(layers)==self.mnet.dimensions
        if layers==():
            layers=self.layers
        return self.mnet._get_strength(self.node,layers)
    def __iter__(self):
        if self.mnet.dimensions>1:
            for node in self.mnet._iter_neighbors(self.node,self.layers):
                yield node #maybe should only return the indices that can change?
        else:
            for node in self.mnet._iter_neighbors(self.node,self.layers):
                yield node[0]
    def layers(self,*layers):
        return MultisliceNode(self.node,self.mnet,layers=layers)

class MultisliceNetworkWithParent(MultisliceNetwork):
    def _set_parent(self,parent):
        self.parent=parent
    def add_node(self,node,dimension):
        self.parent.add_node(node,0)
        MultisliceNetwork.add_node(self,node,dimension)

class CoupledMultiplexNetwork(MultisliceNetwork):
    """
    couplings - A list or tuple with lenght equal to dimensions
                Each coupling must be either a policy or a network
                policy is a tuple: (type, weight)
                policy types: 'ordinal', 'categorical', 'ordinal_warp', 'categorical_warp'
    
    policies by giving inter-slice couplings ??
    """

    def __init__(self,couplings=None,directed=False,noEdge=0):
        self.directed=directed
        self.noEdge=noEdge

        if couplings!=None:
            #assert len(couplings)==dimensions
            self.couplings=[]
            for coupling in couplings:
                if isinstance(coupling,tuple):
                    self.couplings.append(coupling)
                elif isinstance(coupling,MultisliceNetwork):
                    self.couplings.append((coupling,))
                else:
                    raise ValueError("Invalid coupling type: "+str(type(coupling)))
            self.dimensions=len(couplings)+1
        else:
            #couplings=map(lambda x:None,range(dimensions))
            self.dimensions=1

        self._init_slices(self.dimensions)
        
        #diagonal elements, map with keys as tuples of slices and vals as MultiSliceNetwork objects
        #keys are not tuples if dimensions==2
        self.A={} 

    def _get_link_dimension(self,link):
        dims=[]
        for d in range(self.dimensions):
            if link[2*d]!=link[2*d+1]:
                dims.append(d)
        if len(dims)==1:
            return dims[0]
        else:
            return None

    def _get_A_with_tuple(self,layer):
        """Return self.A. Layer must be given as tuple.
        """
        if self.dimensions==2:
            return self.A[layer[0]]
        else:
            return self.A[layer]

    def _add_A(self,node):
        net=MultisliceNetworkWithParent(dimensions=1)
        net._set_parent(self)
        self.A[node]=net

    def add_node(self,node,dimension):
        #overrrides the parent method

        #check if new diagonal matrices needs to be added
        if node not in self.slices[dimension]:
            if dimension>0:            
                if self.dimensions>2:
                    new_slices=list(self.slices[1:])
                    new_slices[dimension-1]=[node]
                    for s in itertools.product(*new_slices):
                        self._add_A(s)
                else:
                    self._add_A(node)


            #call parent method
            MultisliceNetwork.add_node(self,node,dimension)


    def _has_layer_with_tuple(self,layer):
        """Return true if layer in self.A. Layer must be given as tuple.
        """
        if self.dimensions==2:
            return layer[0] in self.A
        else:
            return layer in self.A


    def _get_link(self,link):
        """Overrides parents method.
        """
        #if len(reduce(map(lambda d:link[2*d]!=link[2*d+1],range(self.dimensions))))!=1:
        #    return 0.0 
        d=self._get_link_dimension(link)
        if d!=None:
            if d>0:
                coupling=self.couplings[d-1]                
                if coupling[0]=="categorical":
                    return coupling[1]
                elif isinstance(coupling[0],MultisliceNetwork):
                    return self.couplings[d-1][0][link[2*d],link[2*d+1]]
                else:
                    raise Exception("Coupling not implemented: "+str(coupling))
            else:
                if self._has_layer_with_tuple(link[2::2]):
                    return self._get_A_with_tuple(link[2::2])[link[0],link[1]]
                else:
                    return 0.0
        else:
            return 0.0
                
    def _set_link(self,link,value):
        """Overrides parents method.
        """
        d=self._get_link_dimension(link)
        if d==0:
            S=link[2::2]
            #if not self._has_layer_with_tuple(S):
            #    self._add_layer_with_tuple(S)
            self._get_A_with_tuple(S)[link[0],link[1]]=value
        elif d==None:
            raise KeyError("No self-links.")
        else:
            raise KeyError("Can only set links in the node dimension.")


    def _get_dim_degree(self,node,dimension):
        coupling_type=self.couplings[dimension-1][0]
        if coupling_type=="categorical":
            return len(self.slices[dimension])-1
        elif isinstance(coupling_type,MultisliceNetwork):
            return self.couplings[d-1][0][node[d]].deg()
        else:
            raise NotImplemented()

    def _get_dim_strength(self,node,dimension):
        coupling_str=self.couplings[dimension-1][1]
        coupling_type=self.couplings[dimension-1][0]
        if isinstance(coupling_type,MultisliceNetwork):
            raise Exception() #please implement this
        return self._get_dim_degree(node,dimension)*coupling_str


    def _iter_dim(self,node,dimension):
        coupling_type=self.couplings[dimension-1][0]
        if coupling_type=="categorical":
            for n in self.slices[dimension]:
                if n!=node[dimension]:
                    yield node[:dimension]+(n,)+node[dimension+1:]
        else:
            raise NotImplemented()
        
    def _select_dimensions(self,node,dims):
        if dims==None:
            for d in range(self.dimensions):
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

    def _get_degree(self,node, dims):
        """Overrides parents method.
        """
        k=0
        for d in self._select_dimensions(node,dims):
            if d==0:
                k+=self._get_A_with_tuple(node[1:])[node[0]].deg()
            else:
                k+=self._get_dim_degree(node,d)
        return k

    def _get_strength(self,node, dims):
        """Overrides parents method.
        """
        s=0
        for d in self._select_dimensions(node,dims):
            if d==0:
                s+=self._get_A_with_tuple(node[1:])[node[0]].str()
            else:
                s+=self._get_dim_strength(node,d)
        return s

    def _iter_neighbors(self,node,dims):
        """Overrides parents method.
        """
        for d in self._select_dimensions(node,dims):
            if d==0:                
                for n in self._get_A_with_tuple(node[1:])[node[0]]:
                    yield (n,)+node[1:]
            else:
                for n in self._iter_dim(node,d):
                    yield n


    def get_couplings(self,dimension):
        """Returns a view to a network of couplings between nodes and
        their counterparts in other slices of the given dimension.        
        """
        pass

    def set_connection_policy(self,dimension,policy):
        pass

class FlatMultisliceNetworkView(MultisliceNetwork):
    """

    fnet[(1,'a','b')]
    fnet[(1,'a','b'),(2,'a','b')]

    """
    def __init__(self,mnet):
        self.mnet=mnet
        self.dimensions=1

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

class ModularityMultisliceNetworkView(MultisliceNetwork):
    def __init__(self,mnet,gamma=1.0):
        self.gamma=gamma
        self.mnet=mnet

        self.slices=mnet.slices
        self.dimensions=mnet.dimensions

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
    class FlattenedMultisliceNetworkxView(networkx.Graph):
        pass
except ImportError:
    pass



if __name__ == '__main__':
    import tests.net_test
    tests.net_test.test_net()
