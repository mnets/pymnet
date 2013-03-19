

class MultisliceNetwork(object):
    """

    couplings - A list or tuple with lenght equal to dimensions
                Each couling must be either a policy or a network
                policy is a tuple: (type, weight)
                policy types: ordinal, categorical, ordinal_warp, categorical_warp
    
    policies by giving inter-slice couplings ??

    """
    def __init__(self,
                 dimensions=1,
                 directed=False,
                 couplings=None,
                 intersliceLinks=True):
        #todo: assert that parameters are ok

        self.dimensions=dimensions
        self.directed=directed
        self.intersliceLinks=intersliceLinks

        if couplings!=None:
            assert len(couplings)==dimensions
            self.couplings=[]
            for coupling in couplings:
                if isinstance(coupling,tuple):
                    raise NotImplemented("yet.")
                elif isinstance(coupling,MultisliceNetwork):
                    self.couplings.append(coupling)
                else:
                    raise ValueError("Invalid coupling type: "+str(type(coupling)))
        else:
            couplings=map(lambda x:None,range(dimensions))

        self.slices=[] #set for each dimension
        if directed:
            self.net=networkx.DiGraph()
        else:
            self.net=networkx.Graph()        

        #should keep table of degs and strenghts
        
    def _get_link(self,link):
        #get it first from the net

        #then look at the couplings
        pass

    def __getitem__(self,item):
        """

        dimension=2
        i,s     = node i at slice s
        i,j,s   = link i,j at slice s = i,j,s,s
        i,j,s,r = link i,j between slices s and r

        i,: = multislice node (=iterator,deg etc)
        :,:,s,s = view to slice s

        dimension=3
        i,s,x = node i at slice1 and slice2 x
        i,j,s,x = same as i,j,s,s,x,x
        i,j,s,r,x,y = ...
        """
        d=self.dimensions
        if not isinstance(item,tuple):
            item=(item,)
        if len(item)==d: #node
            pass
        elif len(item)==2*d: #link
            pass
        elif len(item)==d+1: #link
            pass
        else:
            if d>1:
                raise KeyError("%d, %d, or %d indices please."%(d,d+1,2*d))
            else: #d==1
                raise KeyError("1 or 2 indices please.")

    def __setitem__(self,item,val):
        pass
    
    def get_couplings(self,dimension):
        """Returns a view to a network of couplings between nodes and
        their counterparts in other slices of the given dimension.        
        """
        pass

    def add_slice(self,dimension,s):
        pass

    def add_node(self,node):
        pass

    def neighbors(self,*args):
        pass
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

    def set_connection_policy(self,dimension,policy):
        pass

class MultisliceNode(object):
    def __init__(self,mnet,selected_dimension=None):
        """A node in multilice network. If dimension is
        given, then only other nodes in that dimension are
        considered as neighbors of this node.
        """
        pass

class FlatMultisliceNetworkView(object):
    def __init__(self,mnet):
        self.mnet=mnet
        self.dim=0
    def __getitem__(self,a):
        if isinstance(a,tuple):
            if len(a)!=2:
                raise KeyError("Too many indices.")
            return self.mnet[tuple(itertools.chain(*zip(*a)))]
        else: #it must be a list
            return FlatMultisliceNetworkViewNode(self,a)

class FlatMultisliceNetworkViewNode(object):
    pass

class ModularityMultisliceNetworkView(MultisliceNetwork):
    def __init__(self,mnet,alpha=1.0,omega=1.0):
        self.mnet=mnet
        #precalc ms,kis,u
    def __getitem__(self,item):
        if len(item)==2*self.mnet.dimensions:
            v=self.mnet[item]
            if v>0:
                if item[0]!=item[1]: #its inside slice
                    kis=self.mnet.str((item[0],)+item[2::2])
                    kjs=self.mnet.str((item[1],)+item[3::2])
                    ms=None
                    v-alpha*kis*kjs/float(2.0*ms)
                else:
                    return omega*v
            else:
                return v
        else:
            pass
    

try:
    import networkx
    class FlattenedMultisliceNetworkxView(networkx.Graph):
        pass
except ImportError:
    pass
