"""Module which allows one to use Networkx methods for pymnet network objects.
"""

import networkx
import collections
from functools import wraps
from pymnet.net import MultilayerNetwork

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

#NetworkX supports tuples as node names, but pymnet doesn't (because in Python there is no way of distinguishing between net[1,2] and net[(1,2)] ). 
#In order to make some of the NetworkX functions that use tuples and node names to work, we define a new class "ntuple" which is a tuple that is
#used to store node names. 
class ntuple(tuple):
    pass

class MonoplexGraphWrapper_singleedge(MutableMapping):
    def __init__(self,net,node1,node2):
        self.net=net
        self.node1=node1
        self.node2=node2
    def __getitem__(self,key):
        if key=="weight":
            return self.net[self.node1,self.node2]
        else:
            raise KeyError(key)
    def __iter__(self):
        yield "weight"
    def __len__(self):
        return 1

    def __setitem__(self,key,val):
        if key=="weight":
            self.net[self.node1,self.node2]=val
    def __delitem__(self,key):
        if key=="weight":
            self.net[self.node1,self.node2]=self.net.noEdge
    def copy(self):
        return dict( ((k,self[k]) for k in self) ) #dict(self.iteritems())

class MonoplexGraphWrapper_adjlist(MutableMapping):
    def __init__(self,net,node):
        self.net=net
        self.node=node
    def __getitem__(self,key):
        if key.__class__==tuple: key=ntuple(key) 
        key in {} #this is to raise TypeError if key is unhashable
        if key in self.net[self.node]:
            return MonoplexGraphWrapper_singleedge(self.net,self.node,key)
        else:
            raise KeyError(key)
    def __iter__(self):
        for node in self.net[self.node]:
            yield node
    def __len__(self):
        return self.net[self.node].deg()


    def __setitem__(self,key,val):
        if key.__class__==tuple: key=ntuple(key) 
        if isinstance(val,dict) or isinstance(val,MonoplexGraphWrapper_singleedge):
            if len(val)>0:
                #self.net[self.node,key]=list(val.itervalues())[0]
                self.net[self.node,key]=list( (val[key] for key in val))[0]
            else:
                self.net[self.node,key]=1
        else:
            self.net[self.node,key]=val
    def __delitem__(self,key):
        self.net[self.node,key]=self.net.noEdge


class MonoplexGraphWrapper_adj(MutableMapping):
    def __init__(self,net):
        self.net=net
    def __getitem__(self,key):
        if key.__class__==tuple: key=ntuple(key) 
        key in {} #this is to raise TypeError if key is unhashable
        if key in self.net:
            return MonoplexGraphWrapper_adjlist(self.net,key)
        else:
            raise KeyError(key)
    def __iter__(self):
        for node in self.net:
            yield node
    def __len__(self):
        return len(self.net)

    def __setitem__(self,key,val):
        if key.__class__==tuple: key=ntuple(key) 
        if isinstance(val,dict):
            self.net.add_node(key)
            #for key2,val2 in val.iteritems():
            for key2 in val:
                val2=val[key2]
                MonoplexGraphWrapper_adjlist(self.net,key)[key2]=val2
        else:
            raise Exception("Can only sent adjacencies to dicts.")
    def __delitem__(self,key):
        raise Exception("Cannot remove nodes.")


class MonoplexGraphWrapper_node(MutableMapping):
    def __init__(self,net):
        self.net=net
    def __getitem__(self,key):
        if key.__class__==tuple: key=ntuple(key) 
        key in {} #this is to raise TypeError if key is unhashable
        if key in self.net:
            return {}
        else:
            raise KeyError(key)
    def __iter__(self):
        for node in self.net:
            yield node
    def __len__(self):
        return len(self.net)

    def __setitem__(self,key,val):
        pass
    def __delitem__(self,key):
        pass


class MonoplexGraphNetworkxView(networkx.Graph):
    def __init__(self,net=None,data=None,**kwargs):
        super(MonoplexGraphNetworkxView, self).__init__(**kwargs)

        if net==None: #networkx is calling __class__()
            net=MultilayerNetwork(aspects=0)

        self.net=net

        #Networkx Graph class has changed since 2.0
        if int(networkx.__version__.split(".")[0])>=2:
            self._adj=MonoplexGraphWrapper_adj(net)
            self._node=MonoplexGraphWrapper_node(net)
        else:
            self.adj=MonoplexGraphWrapper_adj(net)
            self.edge=MonoplexGraphWrapper_adj(net)
            self.node=MonoplexGraphWrapper_node(net)

        if data is not None:
            networkx.convert.to_networkx_graph(data,create_using=self)

    def fresh_copy(self):
        fresh_net=MultilayerNetwork(aspects=0)
        return MonoplexGraphNetworkxView(fresh_net)


class MonoplexGraphNetworkxNew(MonoplexGraphNetworkxView):
    def __init__(self,data=None,**kwargs):
        net=MultilayerNetwork(aspects=0) #new empty pymnet object
        super(MonoplexGraphNetworkxNew, self).__init__(net,data=data,**kwargs)

def autowrap(net):
    assert net.aspects==0, "Only monoplex networks."
    assert net.directed==False, "Only undirected networks."
    return MonoplexGraphNetworkxView(net)

def networkxdecorator(f):
    @wraps(f)
    def newf(*args, **kwargs):
        #First we wrapt the pyment objects given as parameters
        newargs=[]
        for arg in args:
            if isinstance(arg,MultilayerNetwork):
                newargs.append(autowrap(arg))
            else:
                newargs.append(arg)
        args=tuple(newargs)

        #for key,val in kwargs.iteritems():
        for key in kwargs:
            val=kwargs[key]
            if isinstance(val,MultilayerNetwork):
                kwargs[key]=autowrap(val)
            if val.__class__==tuple: 
                kwargs[key]=ntuple(val) 

        #Modify the NetworkX library such that new graphs are wrapped pymnet objects
        networkx_Graph_original=networkx.Graph
        networkx.Graph=MonoplexGraphNetworkxView

        #Run the actual function
        rval=f(*args, **kwargs)

        #Revert the modifications to NetworkX
        networkx.Graph=networkx_Graph_original

        #Unpack the pymnet objects from the results
        if isinstance(rval,MonoplexGraphNetworkxView):
            rval=rval.net

        return rval

    return newf

#We need to modify the networkx module such that new graphs are wrapped pymnet objects
#import imp
#networkx_modified=imp.load_module('networkx_modified', *imp.find_module('networkx'))
#import networkx as networkx_modified
#networkx_modified.Graph=MonoplexGraphNetworkxNew

for name,obj in networkx.__dict__.items():
    if hasattr(obj,"__call__"):
        exec(name+"=networkxdecorator(obj)")

