"""Module for visualizing multilayer networks.
"""
import pymnet
import random,math

from net import MultiplexNetwork
import netio

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
    netdatastr=netio.write_json(net)

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
        def __init__(self,figsize=None,layergap=1,eps=0.001,padding=0.05):
            self.nodes=[]
            self.layers=[]
            self.edges=[]

            self.padding=padding
            self.eps=eps        
            self.layergap=layergap
            self.figsize=figsize

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

            self.fig=plt.figure(figsize=self.figsize)
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
            self.circle = Circle((self.x, self.y), self.size/2.,color=self.color)        
            self.net.ax.add_patch(self.circle)
            art3d.pathpatch_2d_to_3d(self.circle, z=self.layer.z, zdir="z")
            fix_attr(self.circle,"zorder",self.layer.z+self.net.eps)

            if self.label!=None:
                self.labelObject=self.net.ax.text(self.x+self.size/2.,self.y+self.size/2.,self.layer.z+self.net.eps,str(self.label),**self.labelArgs)
                fix_attr(self.labelObject,"zorder",self.layer.z+2*self.net.eps)

    class Layer(object):
        def __init__(self,net,color="gray",alpha=0.3,shape="rectangle",label=None,labelloc=(1,1)):
            assert shape in ["rectangle","circle"]
            self.shape=shape
            self.color=color
            self.alpha=alpha
            self.label=label
            self.labelloc=labelloc
            self.z=None
            self.net=net
            self.net.register_layer(self)

        def draw(self):
            assert self.z!=None
            if self.shape=="rectangle":
                self.layer=Rectangle((0,0),1,1,alpha=self.alpha,color=self.color)
                if self.label!=None:
                    self.labelObject=self.net.ax.text(self.labelloc[0],self.labelloc[1],self.z,str(self.label))
            elif self.shape=="circle":
                self.layer=Circle((0.5,0.5),0.5,alpha=self.alpha,color=self.color)
                if self.label!=None:
                    self.labelObject=self.net.ax.text(self.labelloc[0],self.labelloc[1],self.z,str(self.label))
            self.net.ax.add_patch(self.layer)
            art3d.pathpatch_2d_to_3d(self.layer, z=self.z, zdir="z")
            fix_attr(self.layer,"zorder",self.z)

    class Edge(object):
        def __init__(self,node1,node2,color="gray",width=1.0,directed=False,style="-",z=0):
            self.node1=node1
            self.node2=node2
            self.net=node1.net
            assert 0<=z<=1
            self.z=z

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
                z=(zs[i]+zs[i+1])/2.+self.z*self.net.eps
                line=self.net.ax.plot(xs[i:i+2],ys[i:i+2],zs=zs[i:i+2],linestyle=self.style,zdir="z",color=self.color,linewidth=self.width)[0]
                fix_attr(line,"zorder",z)
                self.lines.append(line)


    class PropertyAssigner(object):
        rules=set(["order","name","f"])
        def __init__(self,propDict,propRule,defaultProp,net):
            self.propDict=propDict
            self.propRule=propRule
            self.defaultProp=defaultProp
            self.net=net

        def _get_from_property_dict(self,item):
            if item in self.propDict:
                return self.propDict[item]
            else:
                return None

        def __getitem__(self,item):
            pdictval=self._get_from_property_dict(item)
            if pdictval!=None:
                return pdictval
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
            if "f" in self.propRule and self.propRule["rule"]!="f":
                item=self.propRule["f"](item)
            if "scaleby" in self.propRule:
                item=item*self.propRule["scaleby"]
            if "colormap" in self.propRule:
                item=matplotlib.cm.get_cmap(self.propRule["colormap"])(item)
            return item

    class LayerColorAssigner(PropertyAssigner):
        pass

    class LayerAlphaAssigner(PropertyAssigner):
        pass

    class LayerLabelAssigner(PropertyAssigner):
        pass

    class LayerLabelLocAssigner(PropertyAssigner):
        pass

    class LayerOrderAssigner(PropertyAssigner):
        pass

    class NodePropertyAssigner(PropertyAssigner):
        rules=PropertyAssigner.rules.union(set(["degree"]))
        def get_by_rule(self,item,rule):
            if rule=="degree":
                return self.net[item].deg()
            return super(NodePropertyAssigner,self).get_by_rule(item,rule)

    class NodeLabelSizeAssigner(NodePropertyAssigner):
        pass
    class NodeLabelColorAssigner(NodePropertyAssigner):
        pass
    class NodeLabelStyleAssigner(NodePropertyAssigner):
        pass
    class NodeLabelAlphaAssigner(NodePropertyAssigner):
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
            return super(NodeSizeAssigner,self).get_by_rule(item,rule)

        def apply_modify_rules(self,item):
            if "propscale" in self.propRule:
                coeff=self.propRule["propscale"]
                n=len(self.net)     
                item=item*coeff/float(math.sqrt(n))
            return super(NodeSizeAssigner,self).apply_modify_rules(item)


    #nodes todo: marker

    class EdgePropertyAssigner(PropertyAssigner):
        rules=NodePropertyAssigner.rules.union(set(["edgetype","edgeweight"]))

        def _get_from_property_dict(self,item):
            """Return the edge property from the property dict given by the user.

            For directed networks this is same as the parent classes method. For 
            undirected networks both directions for edges are accepted.
            """
            if self.net.directed:
                return super(EdgePropertyAssigner,self)._get_from_property_dict(item)
            else:
                if item in self.propDict:
                    return self.propDict[item]
                else:
                    try:
                        item=(item[1],item[0])
                        if item in self.propDict:
                            return self.propDict[item]
                    except Exception:
                        return None                    
                return None

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

    class EdgeZAssigner(EdgePropertyAssigner):
        pass

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
            else:
                raise Exception("Invalid layout: "+layout)
        else:
            if layout=="random":
                for nl in net.iter_node_layers():
                    nlcoords[nl]=(random.random(),random.random())
            else:
                raise Exception("Invalid layout: "+layout)
        return ncoords,nlcoords         


    def draw(net,layout="spring",layershape="rectangle",azim=-51,elev=22,show=False,layergap=1.0,camera_dist=None,autoscale=True,
             figsize=None,nodeCoords={},nodelayerCoords={},
             layerPadding=0.05,alignedNodes=True,
             layerColorDict={},layerColorRule={},defaultLayerColor="#29b7c1",
             layerAlphaDict={},layerAlphaRule={},defaultLayerAlpha=0.75,
             layerLabelDict={},layerLabelRule={"rule":"name"},defaultLayerLabel=None,
             layerLabelLocDict={},layerLabelLocRule={},defaultLayerLabelLoc=(1,1),
             layerOrderDict={},layerOrderRule={"rule":"name"},defaultLayerOrder=0,
             nodeLabelDict={},nodeLabelRule={"rule":"nodename"},defaultNodeLabel=None,
             nodeLabelSizeDict={},nodeLabelSizeRule={},defaultNodeLabelSize=None,
             nodeLabelColorDict={},nodeLabelColorRule={},defaultNodeLabelColor='k',
             nodeLabelStyleDict={},nodeLabelStyleRule={},defaultNodeLabelStyle="normal",
             nodeLabelAlphaDict={},nodeLabelAlphaRule={},defaultNodeLabelAlpha=1.0,
             nodeSizeDict={},nodeSizeRule={"rule":"scaled","scalecoeff":0.2},defaultNodeSize=None,
             nodeColorDict={},nodeColorRule={},defaultNodeColor="black",
             edgeColorDict={},edgeColorRule={},defaultEdgeColor="gray",
             edgeWidthDict={},edgeWidthRule={},defaultEdgeWidth="1.5",
             edgeZDict={},edgeZRule={},defaultEdgeZ=0,
             edgeStyleDict={},edgeStyleRule={"rule":"edgetype","intra":"-","inter":":"},defaultEdgeStyle="-"):
        """Visualize a multilayer network.

        Creates a 3D pictures of multilayer networks are drawn using Matplotlib. The network can be any type of multilayer
        network with a single aspect.

        Parameters
        ----------
        net : MultilayerNetwork
           Network that is to be drawn
        layout : string
           Layout algorithm. Options are "circular","shell","spring", or "spectral".
        layershape : string
           Shape of the layers. Options are "rectangle" or "circular".
        azim : float
           Azimuth of the layers given in degrees.
        elev : float
           Elevation of the layers given in degrees.
        show : bool
           If true, the picture of the network is displayed using the default Matplotlib backend.
        layergap : float
           The gap between the layers. See also autoscale.
        camera_dist : float, None
           The distance of the camera to the layers. See also autoscale.
        autoscale : bool
           If true, the layergap and camera distance is scaled automatically such that the whole drawing fits the figure.
           This is done if the layergap times 3 is larger than 3.
        figsize : tuple of integers, None
           The figsize argument is forwarded to pyplot.figure when a new figure is created.
        alignedNodes : bool, None
           Should each node have the same coordinate in each layer. If None, then True for multiplex networks and False for multilayer networks.
        layerPadding : float
           Space between nodes and the edge of each layer.
        [property]Dict : dict
           Dictionary giving each element a property value. Keys are the elements and values are the property values.
        [property]Rule : dict
           Rule used to determine the property values if they are not given in the property dictionary. Empty dictionary
           skips this step.
        default[property] : object
           The default value for the property if it is not given in the property dict or by a rule.

        Notes
        -----
        **Setting properties**

        Various visible elements can be set values using a property setting scheme which is similar for all of the following
        properties: layer color, layer label, node labe, node size, node color, edge color, edge width, and edge style.

        Each of each property has three parameters that can be used to set the values of the elements: [property]Dict, [property]Rule,
        and default[property]. (Here the word [property] is replaced by the property name.) Each of these parameters can give a way
        to set a value for property of an element, and the parameters are gone through in the order [property]Dict, [property]Rule,
        and default[property] until a property value is found. 

        The format for defining edges in property dictionaries is tuples with two node-layer names. For example, and edges between node
        1 in layer 'a' and node 2 in layer 'b' is specified with tuple ((1,'a'),(2,'b')).

        All z-coordinate modifiers (e.g., edgeZ) must lie between 0 and 1.

        **Property rules**  
     
        The [property]Rule parameter can be used to set property values by giving a rule for determining the property value. The rules
        can be generic or specific to the property type. For example, using node degree as a property value is specific to node properites
        such as node size or node color. Empty property dictionary means that there is no rule for setting the property, and a rule
        can be set by adding an item to the property rule dictionary with "rule" as a key and value correspoding to the specific rule.

        Generic properties:

        - "order" : Order at which the iterator for the object gives a value of the property. First object gets value 0.
        - "name" : Object name is used as a value for the property
        
        Node properties (node color, node label, node size):

        - "degree" : Degree of the node.

        Node label property:

        - "nodename" : Name of the node (note that "name" returns the node-layer tuple).

        Edge properties (edge color,edge width, edge style):

        - "edgetype" : Properties are given by edge type. You can include keys "intra" and/or "inter" in the property rule dictionary
                       to give values for intra-layer edges and inter-layer edges.
        - "edgeweight" : Weight of the edge.

        **Property modifiers**
    
        Properties generated by rules can be modified before they are assigined as final properties of the elements. This is
        done by property modifiers and it is useful for example when converting numeric values to colors. Property modifiers
        can be stacked and they are evaluated in an order that is reverse to the order in which they are introduced next. Each
        property modifier is an item in the property rule dictionary. 

        Generic modifiers:

        - "colormap" : Use a Matplotlib color map to map a number to a color. Value is the colormap name, e.g. "jet".
        - "scaleby" : Multiply the property values by a constant given by the value
        - "f" : Any function take takes the value as an argument an returns the modified value

        Node size modifiers:

        - "propscale" : Multiply everytnig by a constant given as value and divide by the sqrt of the number of nodes in the net.
        """

        assert net.aspects==1

        #Get coordinates
        ncoords,nlcoords=get_layout(layout,net,alignedNodes=alignedNodes)

        for node,coord in nodeCoords.items():
             ncoords[node]=coord
        for nl,coord in nodelayerCoords.items():
             nlcoords[nl]=coord

        #Initialize assigners
        layerColor=LayerColorAssigner(layerColorDict,layerColorRule,defaultLayerColor,net)
        layerAlpha=LayerAlphaAssigner(layerAlphaDict,layerAlphaRule,defaultLayerAlpha,net)
        layerLabel=LayerLabelAssigner(layerLabelDict,layerLabelRule,defaultLayerLabel,net)
        layerLabelLoc=LayerLabelLocAssigner(layerLabelLocDict,layerLabelLocRule,defaultLayerLabelLoc,net)
        layerOrder=LayerOrderAssigner(layerOrderDict,layerOrderRule,defaultLayerOrder,net)
        nodeLabel=NodeLabelAssigner(nodeLabelDict,nodeLabelRule,defaultNodeLabel,net)
        nodeLabelSize=NodeLabelSizeAssigner(nodeLabelSizeDict,nodeLabelSizeRule,defaultNodeLabelSize,net)
        nodeLabelColor=NodeLabelColorAssigner(nodeLabelColorDict,nodeLabelColorRule,defaultNodeLabelColor,net)
        nodeLabelStyle=NodeLabelStyleAssigner(nodeLabelStyleDict,nodeLabelStyleRule,defaultNodeLabelStyle,net)
        nodeLabelAlpha=NodeLabelAlphaAssigner(nodeLabelAlphaDict,nodeLabelAlphaRule,defaultNodeLabelAlpha,net)
        nodeSize=NodeSizeAssigner(nodeSizeDict,nodeSizeRule,defaultNodeSize,net)
        nodeColor=NodeColorAssigner(nodeColorDict,nodeColorRule,defaultNodeColor,net)
        edgeColor=EdgeColorAssigner(edgeColorDict,edgeColorRule,defaultEdgeColor,net)
        edgeWidth=EdgeWidthAssigner(edgeWidthDict,edgeWidthRule,defaultEdgeWidth,net)
        edgeStyle=EdgeStyleAssigner(edgeStyleDict,edgeStyleRule,defaultEdgeStyle,net)
        edgeZ=EdgeZAssigner(edgeZDict,edgeZRule,defaultEdgeZ,net)


        #Build the network
        layers={}
        nodes={}
        nf=NetFigure(figsize=figsize,layergap=layergap,padding=layerPadding)
        for layer in sorted(net.iter_layers(),key=lambda l:layerOrder[l]):
            layers[layer]=Layer(nf,shape=layershape,color=layerColor[layer],label=layerLabel[layer],alpha=layerAlpha[layer],labelloc=layerLabelLoc[layer])

        for nl in net.iter_node_layers():
            if nl in nlcoords:
                xy=nlcoords[nl]
            elif nl[0] in ncoords:
                xy=ncoords[nl[0]]
            else:
                xy=(random.random(),random.random())
            nodeLabelArgs={"size":nodeLabelSize[nl],"color":nodeLabelColor[nl],"style":nodeLabelStyle[nl],"alpha":nodeLabelAlpha[nl]}
            nodes[nl]=Node(layers[nl[1]],xy[0],xy[1],label=nodeLabel[nl],color=nodeColor[nl],size=nodeSize[nl],labelArgs=nodeLabelArgs)

        for nl1 in net.iter_node_layers():
            for nl2 in net[nl1]:
                Edge(nodes[nl1],nodes[nl2],color=edgeColor[(nl1,nl2)],width=edgeWidth[(nl1,nl2)],style=edgeStyle[(nl1,nl2)],z=edgeZ[(nl1,nl2)])

        nf.draw()
        nf.ax.azim=azim
        nf.ax.elev=elev
        if camera_dist!=None:
            nf.ax.dist=camera_dist
        if autoscale and len(layers)*layergap>3:
            nf.ax.autoscale_view()
        if show:
            plt.show()
        return nf.fig
except ImportError:
    print "Warning: cannot import matplotlib."

