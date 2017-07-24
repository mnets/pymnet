"""Classes that are used by the represent multilayer networks and drawing backends to visualize them.
"""

class NetFigure(object):    
    def __init__(self,figsize=None,layergap=1,eps=0.001,padding=0.05,azim=-51,elev=22,show=False,camera_dist=None,autoscale=True):
        self.nodes=[]
        self.layers=[]
        self.edges=[]

        self.padding=padding
        self.eps=eps        
        self.layergap=layergap
        self.figsize=figsize
        self.azim=azim
        self.elev=elev
        self.show=show
        self.camera_dist=camera_dist
        self.autoscale=autoscale

    def normalize_coords(self):
        maxx,maxy,minx,miny=float("-inf"),float("-inf"),float("inf"),float("inf")
        for node in self.nodes:
            if maxx<node.x+node.size/2.: maxx=node.x+node.size/2.
            if maxy<node.y+node.size/2.: maxy=node.y+node.size/2.
            if minx>node.x-node.size/2.: minx=node.x-node.size/2.
            if miny>node.y-node.size/2.: miny=node.y-node.size/2.

        xtrans=lambda x:(x-minx+self.padding)/float(maxx-minx+2*self.padding)
        ytrans=lambda y:(y-miny+self.padding)/float(maxy-miny+2*self.padding)

        for node in self.nodes:
            node.x=xtrans(node.x)
            node.y=ytrans(node.y)


    def draw_elements(self):
        for i,layer in enumerate(self.layers):
            layer.z=i*self.layergap
            if layer.alpha!=0:
                layer.draw()

        for node in self.nodes:
            if node.size>0:
                node.draw()

        for edge in self.edges:
            edge.draw()


    def draw(self,**kwargs):
        #Override this method
        raise NotImplemented()

    def register_layer(self,layer):
        self.layers.insert(0,layer) #First to top
    def register_node(self,node):
        self.nodes.append(node)
    def register_edge(self,edge):
        self.edges.append(edge)

class Node(object):
    def __init__(self,layer,x,y,label=None,size=0.04,color="black",labelArgs={}):
        self.x,self.y,self.size,self.color,self.label=x,y,size,color,label
        self.layer=layer
        self.net=layer.net
        self.label=label
        self.labelArgs=labelArgs 

        self.net.register_node(self)        

    def draw(self):
        #Override this method
        raise NotImplemented()


class Layer(object):
    def __init__(self,net,color="gray",alpha=0.3,shape="rectangle",label=None,labelloc=(1,1),labelArgs={}):
        assert shape in ["rectangle","circle"]
        self.shape=shape
        self.color=color
        self.alpha=alpha
        self.label=label
        self.labelloc=labelloc
        self.labelArgs=labelArgs 
        self.z=None
        self.net=net
        self.net.register_layer(self)

    def draw(self):
        #Override this method
        raise NotImplemented()


class Edge(object):
    def __init__(self,node1,node2,color="gray",width=1.0,directed=False,style="-",z=0,alpha=1):
        self.node1=node1
        self.node2=node2
        self.net=node1.net
        assert 0<=z<=1
        self.z=z
        assert 0<=alpha<=1
        self.alpha=alpha

        self.net.register_edge(self)

        self.color,self.width,self.directed,self.style=color,width,directed,style
