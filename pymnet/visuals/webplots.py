"""Module for creating plots of multiplex network for the web. This is completely separate functionality from the draw function.
"""
import random,math

import pymnet
from pymnet.net import MultiplexNetwork
from .. import netio

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
        if isinstance(outputfile,"".__class__) or isinstance(outputfile,u"".__class__):
            outputfile=open(outputfile,'w')

        outputfile.write("<html><body>")
        outputfile.write(script)
        outputfile.write("</body></html>")
        outputfile.close()
