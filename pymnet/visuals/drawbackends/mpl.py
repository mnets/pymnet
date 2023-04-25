"""Matplotlib backend for the draw method.
"""
from .. import drawnet

import matplotlib

#Checking if we can display graphics.
import os
if os.environ.get("DISPLAY","")=="":
    matplotlib.use("Agg")

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


class NetFigureMPL(drawnet.NetFigure):
    def draw(self, **kwargs):
        ax=kwargs["ax"] if "ax" in kwargs else None

        self.normalize_coords()

        if ax == None:
            self.fig=plt.figure(figsize=self.figsize)
            self.ax=self.fig.add_subplot(projection='3d')
        else:
            assert isinstance(ax,Axes3D), "The axes need to have 3D projection. Use, for example, fig.add_subplot(111, projection='3d')"
            self.ax = ax
            self.fig = self.ax.get_figure()

        self.draw_elements()

        self.ax.set_xlim3d(0, 1)
        self.ax.set_ylim3d(0, 1)
        self.ax.set_zlim3d(0, 2)
        self.ax.set_axis_off()

        fix_attr_range(self.ax,"elev",[0,179])


        self.ax.azim=self.azim
        self.ax.elev=self.elev
        if self.camera_dist!=None:
            self.ax.dist=self.camera_dist
        if self.autoscale and len(self.layers)*self.layergap>3:
            self.ax.autoscale_view()
        if self.show:
            plt.show()

        return self.fig


class NodeMPL(drawnet.Node):
     def draw(self):
        self.circle = Circle((self.x, self.y), self.size/2.,color=self.color)        
        self.net.ax.add_patch(self.circle)
        art3d.pathpatch_2d_to_3d(self.circle, z=self.layer.z, zdir="z")
        fix_attr(self.circle,"zorder",self.layer.z+self.net.eps)

        if self.label!=None:
            self.labelObject=self.net.ax.text(self.x+self.size/2.,self.y+self.size/2.,self.layer.z+self.net.eps,str(self.label),**self.labelArgs)
            fix_attr(self.labelObject,"zorder",self.layer.z+2*self.net.eps)

class LayerMPL(drawnet.Layer):
    def draw(self):
        assert self.z!=None
        if self.shape=="rectangle":
            self.layer=Rectangle((0,0),1,1,alpha=self.alpha,color=self.color)
            if self.label!=None:
                self.labelObject=self.net.ax.text(self.labelloc[0],self.labelloc[1],self.z,str(self.label),**self.labelArgs)
        elif self.shape=="circle":
            self.layer=Circle((0.5,0.5),0.5,alpha=self.alpha,color=self.color)
            if self.label!=None:
                self.labelObject=self.net.ax.text(self.labelloc[0],self.labelloc[1],self.z,str(self.label),**self.labelArgs)
        self.net.ax.add_patch(self.layer)
        art3d.pathpatch_2d_to_3d(self.layer, z=self.z, zdir="z")
        fix_attr(self.layer,"zorder",self.z)

class EdgeMPL(drawnet.Edge):
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
            line=self.net.ax.plot(xs[i:i+2],ys[i:i+2],zs=zs[i:i+2],linestyle=self.style,zdir="z",color=self.color,linewidth=self.width,alpha=self.alpha)[0]
            fix_attr(line,"zorder",z)
            self.lines.append(line)
