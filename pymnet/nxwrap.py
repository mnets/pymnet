"""Module which allows one to use Networkx methods for pymnet network objects.
"""

import networkx
import collections
from functools import wraps
from net import MultilayerNetwork

class MonoplexGraphWrapper_singleedge(collections.MutableMapping):
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
        return dict(self.iteritems())

class MonoplexGraphWrapper_adjlist(collections.MutableMapping):
    def __init__(self,net,node):
        self.net=net
        self.node=node
    def __getitem__(self,key):
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
        if isinstance(val,dict) or isinstance(val,MonoplexGraphWrapper_singleedge):
            if len(val)>0:
                self.net[self.node,key]=list(val.itervalues())[0]
            else:
                self.net[self.node,key]=1
        else:
            self.net[self.node,key]=val
    def __delitem__(self,key):
        self.net[self.node,key]=self.net.noEdge


class MonoplexGraphWrapper_adj(collections.MutableMapping):
    def __init__(self,net):
        self.net=net
    def __getitem__(self,key):
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
        if isinstance(val,dict):
            self.net.add_node(key)
            for key2,val2 in val.iteritems():
                MonoplexGraphWrapper_adjlist(self.net,key)[key2]=val2
        else:
            raise Exception("Can only sent adjacencies to dicts.")
    def __delitem__(self,key):
        raise Exception("Cannot remove nodes.")


class MonoplexGraphWrapper_node(collections.MutableMapping):
    def __init__(self,net):
        self.net=net
    def __getitem__(self,key):
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
    def __init__(self,net,**kwargs):
        super(MonoplexGraphNetworkxView, self).__init__(**kwargs)

        self.net=net
        self.adj=MonoplexGraphWrapper_adj(net)
        self.edge=MonoplexGraphWrapper_adj(net)
        self.node=MonoplexGraphWrapper_node(net)
        self.graph={}

class MonoplexGraphNetworkxNew(MonoplexGraphNetworkxView):
    def __init__(self,**kwargs):
        net=MultilayerNetwork(aspects=0) #new empty pymnet object
        super(MonoplexGraphNetworkxNew, self).__init__(net,**kwargs)

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

        for key,val in kwargs.iteritems():
            if isinstance(val,MultilayerNetwork):
                kwargs[key]=autowrap(val)

        #Modify the NetworkX library such that new graphs are wrapped pymnet objects
        networkx_Graph_original=networkx.Graph
        networkx.Graph=MonoplexGraphNetworkxNew

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

for name,obj in networkx.__dict__.iteritems():
    if hasattr(obj,"__call__"):
        exec(name+"=networkxdecorator(obj)")

