"""Module for visualizing multilayer networks.
"""
import pymnet
import random,math

from net import MultiplexNetwork
import io

webplot_template="""
<script src="http://d3js.org/d3.v3.min.js"></script>
<script>
 var mpnet = JSON.parse('@netjson');

 var color = d3.scale.category20();
 var svg_layer=[];
 var node_layer=[];
 var link_layer=[];
 var layer_label=[];

 // Calculate size for the figure
 var width = Math.sqrt(mpnet.nodes.length)*70;//500;
 var height = 4/6*width;
 var fontsize=Math.max(width*0.05,16)

 var force = d3.layout.force()
                      .charge(-120)
                      .linkDistance(30)
                      .size([width, height])
                      .nodes(mpnet.nodes)
                      .links(mpnet.links)
                      .start();

 var nlayers=mpnet.layers.length;

 for (var layer=nlayers-1;layer>=0;layer--){
  svg_layer[layer] = d3.select("body").append("svg")
                     .attr("layer",0)
                     .style("position","absolute")
                     .style("left","100px")
                     .style("top",(width/6+layer*width/4).toString()+"px")
                     .style("background-color","rgba(100,100,100,0.3)")
                     .style("transform","rotate3D(-0.9,0.4,0.4,70deg)") // Firefox
                     .style("-webkit-transform","rotate3D(-0.9,0.4,0.4,70deg)") // Safari, Chrome 
                     .attr("width", width)
                     .attr("height", height);

  layer_label[layer]=svg_layer[layer].selectAll(".layerlabel")
                     .data([mpnet.layers[layer]])
                     .enter()
                     .append("text")
                     .text(function(d){return d.name;})
                     .attr("dx",function(d){return width-0.8*d.name.toString().length*fontsize;})
                     .attr("dy",fontsize)
                     .style("font-size",fontsize+"px")
                     .style("fontcolor","black")

  link_layer[layer] = svg_layer[layer].selectAll(".link")
                      .data(mpnet.links)
                      .enter()
                      .append("line")
                      .filter(function(d){return d.layer==layer})
                      .attr("class", "link")
                      .style("stroke-width", function(d) { return 2*Math.sqrt(d.value); })
                      .style("stroke","#999");

  node_layer[layer] = svg_layer[layer].selectAll(".node")
                      .data(mpnet.nodes)
                      .enter().append("circle")
                      .attr("class", "node")
                      .attr("r", 5)
                      .style("fill", function(d) {return color(d.index); })
                      .style("stroke","#fff")
                      .style("stroke-width","1.5px")
                      .call(force.drag);

  node_layer[layer].append("title")
                   .text(function(d) { return d.name; });
 }

 force.on("tick", function() {
  for (var layer=0;layer<nlayers;layer++){
   link_layer[layer].attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });

   node_layer[layer].attr("cx", function(d) { return d.x; })
                    .attr("cy", function(d) { return d.y; });
  }
 });
</script>
"""

def webplot(net,outputfile=None):
    """Create a 3D visualization of a multiplex network for web using D3.

    Creates a webpage that contains a visualization of the input multiplex
    network. The network must have only a single aspect. 

    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    outputfile : None, string, or file object
       Returns the output as a string if outputfile is None. If outputfile
       is string, then uses it as a file name and tries to open it for 
       writing. Finally, if outputfile is a file object then writes to that
       file.

    Returns
    -------
    String or None
       Returns the output as a string if outputfile is None.
    """
    assert isinstance(net,MultiplexNetwork)
    assert net.aspects==1

    script=webplot_template
    netdatastr=io.write_json(net)

    replace={"@netjson" : netdatastr}
    for key,val in replace.items():
        script=script.replace(key,val)
    
    if outputfile==None:
        return script
    else:
        if isinstance(outputfile,str) or isinstance(outputfile,unicode):
            outputfile=open(outputfile,'w')

        outputfile.write("<html><body>")
        outputfile.write(script)
        outputfile.write("</body></html>")
        outputfile.close()

###########
try:
    import matplotlib
    from mpl_toolkits.mplot3d import Axes3D 
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle,PathPatch,Rectangle
    from mpl_toolkits.mplot3d import art3d

    defaultLayerColors=["red","green","blue"]

    def fix_attr(obj,attr,val):
        obj.__setattr__(attr,val) #Just in case there is side effects
        newclass=type(type(obj).__name__,(type(obj),),{})
        setattr(newclass,attr,property(lambda s:val,lambda s,x:None))
        obj.__class__=newclass

    def fix_attr_range(obj,attr,ran):
        assert ran[0]<=obj.__getattribute__(attr)<=ran[1]
        obj.__setattr__("_"+attr,obj.__getattribute__(attr))
        oldclass=type(obj)
        newclass=type(oldclass.__name__,(oldclass,),{})
        def setter(s,val):
            if val<ran[0]:
                val=ran[0]
            elif val>ran[1]:
                val=ran[1]
            obj.__setattr__("_"+attr,val)
        def getter(s):
            return obj.__getattribute__("_"+attr)

        setattr(newclass,attr,property(getter,setter))
        obj.__class__=newclass


    class NetFigure(object):    
        def __init__(self,layergap=1,eps=0.001,padding=0.05):
            self.nodes=[]
            self.layers=[]
            self.edges=[]

            self.padding=padding
            self.eps=eps        
            self.layergap=layergap

        def normalize_coords(self):
            maxx,maxy,minx,miny=0,0,0,0
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

        def draw(self):
            self.normalize_coords()

            self.fig=plt.figure()
            self.ax=self.fig.gca(projection='3d')

            for i,layer in enumerate(self.layers):
                layer.z=i*self.layergap
                layer.draw()

            for node in self.nodes:
                node.draw()

            for edge in self.edges:
                edge.draw()

            self.ax.set_xlim3d(0, 1)
            self.ax.set_ylim3d(0, 1)
            self.ax.set_zlim3d(0, 2)
            self.ax.set_axis_off()

            fix_attr_range(self.ax,"elev",[0,179])

        def register_layer(self,layer):
            self.layers.append(layer)
        def register_node(self,node):
            self.nodes.append(node)
        def register_edge(self,edge):
            self.edges.append(edge)

    class Node(object):
        def __init__(self,layer,x,y,label=None,size=0.04,color="black"):
            self.x,self.y,self.size,self.color,self.label=x,y,size,color,label
            self.layer=layer
            self.net=layer.net
            self.label=label

            self.net.register_node(self)        

        def draw(self):
            self.circle = Circle((self.x, self.y), self.size/2.,color=self.color)        
            self.net.ax.add_patch(self.circle)
            art3d.pathpatch_2d_to_3d(self.circle, z=self.layer.z, zdir="z")
            fix_attr(self.circle,"zorder",self.layer.z+self.net.eps)

            if self.label!=None:
                self.labelObject=self.net.ax.text(self.x+self.size/2.,self.y+self.size/2.,self.layer.z+self.net.eps,str(self.label))
                fix_attr(self.labelObject,"zorder",self.layer.z+self.net.eps)

    class Layer(object):
        def __init__(self,net,color="gray",alpha=0.3,shape="rectangle",label=None):
            assert shape in ["rectangle","circle"]
            self.shape=shape
            self.color=color
            self.alpha=alpha
            self.label=label
            self.z=None
            self.net=net
            self.net.register_layer(self)

        def draw(self):
            assert self.z!=None
            if self.shape=="rectangle":
                self.layer=Rectangle((0,0),1,1,alpha=self.alpha,color=self.color)
                self.labelObject=self.net.ax.text(1,1,self.z,str(self.label))
            elif self.shape=="circle":
                self.layer=Circle((0.5,0.5),0.5,alpha=self.alpha,color=self.color)
                self.labelObject=self.net.ax.text(1,1,self.z,str(self.label))
            self.net.ax.add_patch(self.layer)
            art3d.pathpatch_2d_to_3d(self.layer, z=self.z, zdir="z")
            fix_attr(self.layer,"zorder",self.z)

    class Edge(object):
        def __init__(self,node1,node2,color="gray",width=1.0,directed=False,style="-"):
            self.node1=node1
            self.node2=node2
            self.net=node1.net

            self.net.register_edge(self)

            self.color,self.width,self.directed,self.style=color,width,directed,style

        def draw(self):
            self.lines=[]
            #find layers this edge is crossing
            if abs(self.node1.layer.z - self.node2.layer.z)>self.net.layergap:
                n=int(round(abs(self.node1.layer.z - self.node2.layer.z)/float(self.net.layergap)))+1
                import numpy
                xs=numpy.linspace(self.node1.x,self.node2.x,n)
                ys=numpy.linspace(self.node1.y,self.node2.y,n)
                zs=numpy.linspace(self.node1.layer.z,self.node2.layer.z,n)
                zorders=[]
                for i in range(len(zs)-1):
                    zorders=(zs[i]+zs[i+1])/2.
            else:
                xs=[self.node1.x,self.node2.x]
                ys=[self.node1.y,self.node2.y]
                zs=[self.node1.layer.z,self.node2.layer.z]
            for i in range(len(zs)-1):
                z=(zs[i]+zs[i+1])/2.
                line=self.net.ax.plot(xs[i:i+2],ys[i:i+2],zs=zs[i:i+2],linestyle=self.style,zdir="z",color=self.color,linewidth=self.width)[0]
                fix_attr(line,"zorder",z)
                self.lines.append(line)


    class PropertyAssigner(object):
        rules=set(["order","name"])
        def __init__(self,propDict,propRule,defaultProp,net):
            self.propDict=propDict
            self.propRule=propRule
            self.defaultProp=defaultProp
            self.net=net

        def __getitem__(self,item):
            if item in self.propDict:
                return self.propDict[item]
            elif len(self.propRule)>0:
                assert "rule" in self.propRule
                if self.propRule["rule"] in self.rules:
                    return self.apply_modify_rules(self.get_by_rule(item,self.propRule["rule"]))
                else:
                    raise Exception("Unknown rule: "+str(self.propRule["rule"]))
            else:
                return self.defaultProp

        def get_by_rule(self,item,rule):
            if rule=="order":
                assert "sequence" in self.propRule
                if hasattr(self,"i"):
                    self.i+=1
                else:
                    self.i=0
                return self.propRule["sequence"][self.i%len(self.propRule["sequence"])]
            elif rule=="name":
                return item

        def apply_modify_rules(self,item):
            if "scaleby" in self.propRule:
                item=item*self.propRule["scaleby"]
            if "colormap" in self.propRule:
                item=matplotlib.cm.get_cmap(self.propRule["colormap"])(item)
            return item

    class LayerColorAssigner(PropertyAssigner):
        pass

    class LayerLabelAssigner(PropertyAssigner):
        pass

    class NodePropertyAssigner(PropertyAssigner):
        pass

    class NodeLabelAssigner(NodePropertyAssigner):
        rules=NodePropertyAssigner.rules.union(set(["nodename"]))
        def get_by_rule(self,item,rule):
            if rule=="nodename":
                return item[0]
            return super(NodeLabelAssigner,self).get_by_rule(item,rule)

    class NodeColorAssigner(NodePropertyAssigner):
        rules=NodePropertyAssigner.rules-set(["name"])

    class NodeSizeAssigner(NodePropertyAssigner):
        rules=NodePropertyAssigner.rules.union(set(["scaled"]))-set(["name"])
        def get_by_rule(self,item,rule):
            if rule=="scaled":
                coeff=self.propRule["scalecoeff"] if "scalecoeff" in self.propRule else 1.0
                n=len(self.net)     
                return coeff/float(math.sqrt(n))
            return super(NodeLabelAssigner,self).get_by_rule(item,rule)

    #nodes todo: marker

    class EdgePropertyAssigner(PropertyAssigner):
        rules=NodePropertyAssigner.rules.union(set(["edgetype","edgeweight"]))
        def get_by_rule(self,item,rule):
            if rule=="edgetype":
                if "intra" in self.propRule and item[0][1]==item[1][1]:
                    return self.propRule["intra"]
                elif "inter" in self.propRule and item[0][1]!=item[1][1]:
                    return self.propRule["inter"]
            elif rule=="edgeweight":
                return self.net[item[0]][item[1]]

    class EdgeWidthAssigner(EdgePropertyAssigner):
        pass

    class EdgeColorAssigner(EdgePropertyAssigner):
        pass

    class EdgeStyleAssigner(EdgePropertyAssigner):
        pass


    def draw(net,layout="random",layershape="rectangle",azim=-51,elev=22,show=False,
             layerColorDict={},layerColorRule={"rule":"order","sequence":defaultLayerColors},defaultLayerColor="gray",
             layerLabelDict={},layerLabelRule={"rule":"name"},defaultLayerLabel=None,
             nodeLabelDict={},nodeLabelRule={"rule":"nodename"},defaultNodeLabel=None,
             nodeSizeDict={},nodeSizeRule={"rule":"scaled","scalecoeff":0.2},defaultNodeSize=None,
             nodeColorDict={},nodeColorRule={},defaultNodeColor="black",
             edgeColorDict={},edgeColorRule={},defaultEdgeColor="gray",
             edgeWidthDict={},edgeWidthRule={},defaultEdgeWidth="1.0",
             edgeStyleDict={},edgeStyleRule={"rule":"edgetype","intra":"-","inter":"--"},defaultEdgeStyle="-"):

        assert net.aspects==1

        #Get coordinates
        ncoords,nlcoords={},{}
        if isinstance(net,pymnet.net.MultiplexNetwork):
            if layout in ["circular","shell","spring","spectral"]: #nx layout
                if hasattr(pymnet,"nx"):
                    la=getattr(pymnet.nx,layout+"_layout")
                    na=pymnet.transforms.aggregate(net,1)
                    ncoords=la(na)
                else:
                    raise Exception("Networkx needs to be installed to use layout: "+layout)
            elif layout=="random":
                for node in net:
                    ncoords[node]=(random.random(),random.random())
            else:
                raise Exception("Invalid layout: "+layout)
        elif isinstance(net,pymnet.net.MultilayerNetwork):
            if layout=="random":
                for nl in net.iter_node_layers():
                    nlcoords[nl]=(random.random(),random.random())

        #Initialize assigners
        layerColor=LayerColorAssigner(layerColorDict,layerColorRule,defaultLayerColor,net)
        layerLabel=LayerLabelAssigner(layerLabelDict,layerLabelRule,defaultLayerLabel,net)
        nodeLabel=NodeLabelAssigner(nodeLabelDict,nodeLabelRule,defaultNodeLabel,net)
        nodeSize=NodeSizeAssigner(nodeSizeDict,nodeSizeRule,defaultNodeSize,net)
        nodeColor=NodeColorAssigner(nodeColorDict,nodeColorRule,defaultNodeColor,net)
        edgeColor=EdgeColorAssigner(edgeColorDict,edgeColorRule,defaultEdgeColor,net)
        edgeWidth=EdgeWidthAssigner(edgeWidthDict,edgeWidthRule,defaultEdgeWidth,net)
        edgeStyle=EdgeStyleAssigner(edgeStyleDict,edgeStyleRule,defaultEdgeStyle,net)


        #Build the network
        layers={}
        nodes={}
        nf=NetFigure()
        for layer in net.iter_layers():
            layers[layer]=Layer(nf,shape=layershape,color=layerColor[layer],label=layerLabel[layer])

        for nl in net.iter_node_layers():
            if nl in nlcoords:
                xy=nlcoords[nl]
            elif nl[0] in ncoords:
                xy=ncoords[nl[0]]
            else:
                xy=(random.random(),random.random())
            nodes[nl]=Node(layers[nl[1]],xy[0],xy[1],label=nodeLabel[nl],color=nodeColor[nl],size=nodeSize[nl])

        for nl1 in net.iter_node_layers():
            for nl2 in net[nl1]:
                Edge(nodes[nl1],nodes[nl2],color=edgeColor[(nl1,nl2)],width=edgeWidth[(nl1,nl2)],style=edgeStyle[(nl1,nl2)])

        nf.draw()
        nf.ax.azim=azim
        nf.ax.elev=elev
        if show:
            plt.show()
        return nf.fig
except ImportError:
    print "Warning: cannot import matplotlib."

