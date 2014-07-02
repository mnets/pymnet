"""Module which allows one to use Networkx methods for pymnet network objects.
"""

import networkx
import collections
from functools import wraps
from net import MultilayerNetwork

class MonoplexGraphWrapper_singleedge(collections.Mapping):
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

class MonoplexGraphWrapper_adjlist(collections.Mapping):
    def __init__(self,net,node):
        self.net=net
        self.node=node
    def __getitem__(self,key):
        if key in self.net[self.node]:
            return MonoplexGraphWrapper_singleedge(self.net,self.node,key)
        else:
            raise KeyError(key)
    def __iter__(self):
        for node in self.net[self.node]:
            yield node
    def __len__(self):
        return self.net[self.node].deg()

class MonoplexGraphWrapper_adj(collections.Mapping):
    def __init__(self,net):
        self.net=net
    def __getitem__(self,key):
        if key in self.net:
            return MonoplexGraphWrapper_adjlist(self.net,key)
        else:
            raise KeyError(key)
    def __iter__(self):
        for node in self.net:
            yield node
    def __len__(self):
        return len(self.net)


class MonoplexGraphWrapper_node(collections.Mapping):
    def __init__(self,net):
        self.net=net
    def __getitem__(self,key):
        if key in self.net:
            return {}
        else:
            raise KeyError(key)
    def __iter__(self):
        for node in net:
            yield node
    def __len__(self):
        return len(self.net)


class MonoplexGraphNetworkxView(networkx.Graph):
    def __init__(self,net):
        #call the super constructor?

        self.net=net
        self.adj=MonoplexGraphWrapper_adj(net)
        self.edge=MonoplexGraphWrapper_adj(net)
        self.node=MonoplexGraphWrapper_node(net)
        self.graph={}


def autowrap(net):
    assert net.aspects==0, "Only monoplex networks."
    assert net.directed==False, "Only undirected networks."
    return MonoplexGraphNetworkxView(net)

def networkxdecorator(f):
    @wraps(f)
    def newf(*args, **kwargs):
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

        return f(*args, **kwargs)

    return newf

for name,obj in networkx.__dict__.iteritems():
    if hasattr(obj,"__call__"):
        exec(name+"=networkxdecorator(obj)")
