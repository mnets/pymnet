"""Backend for multilayer network draw method using three.js.

This is still experimental and is missing many features.
"""

from .. import drawnet
from .. import drawbackends
import os

TEMPLATE_FILE=os.path.join( os.path.dirname(drawbackends.__file__),"threejs_template.html")
SIZE=100

class NetFigureThreeJS(drawnet.NetFigure):
    def draw(self,**kwargs):
        self.normalize_coords()

        template_file=open(TEMPLATE_FILE,"r")
        self.template=template_file.read()
        template_file.close()
        
        self.node_snippets=[]
        self.edge_snippets=[]
        self.layer_snippets=[]
        
        self.draw_elements()

        self.template=self.template.replace("@nodes","".join(self.node_snippets) )
        self.template=self.template.replace("@edges","".join(self.edge_snippets))
        self.template=self.template.replace("@layers","".join(self.layer_snippets))

        return self.template
        
class NodeThreeJS(drawnet.Node):
    def draw(self):
        snippet="""
        var node= getNode(@x,@y,@z,@r);
        scene.add(node);

        """
        snippet=snippet.replace("@x",str(SIZE*self.x))
        snippet=snippet.replace("@y",str(10*SIZE*self.y))
        snippet=snippet.replace("@z",str(10*SIZE*self.layer.z))
        snippet=snippet.replace("@r",str(0.1*self.size/2.))

        self.net.node_snippets.append(snippet)

class EdgeThreeJS(drawnet.Edge):
    def draw(self):
        snippet="""
        var link= getLink(@x1,@y1,@z1,@x2,@y2,@z2,@r);
        scene.add(link);

        """
        snippet=snippet.replace("@x1",str(SIZE*self.node1.x))
        snippet=snippet.replace("@y1",str(SIZE*self.node1.y))
        snippet=snippet.replace("@z1",str(SIZE*self.node1.layer.z))

        snippet=snippet.replace("@x2",str(SIZE*self.node2.x))
        snippet=snippet.replace("@y2",str(SIZE*self.node2.y))
        snippet=snippet.replace("@z2",str(SIZE*self.node2.layer.z))

        snippet=snippet.replace("@r",str(0.01))

        self.net.edge_snippets.append(snippet)


class LayerThreeJS(drawnet.Layer):
    def draw(self):
        pass

