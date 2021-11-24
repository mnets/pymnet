"""Property assigners that give a friendly user interface for setting properties of various elements of the networks.
"""

import math

#Some assigner features use matplotlib. These features are only available if matplotlib can be loaded
try:
    import matplotlib
    matplotlib_loaded=True
except ImportError:
    matplotlib_loaded=False

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
            assert "rule" in self.propRule, "The rule dictionary must contain 'rule' key"
            if self.propRule["rule"] in self.rules:
                return self.apply_modify_rules(self.get_by_rule(item,self.propRule["rule"]),item)
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

    def apply_modify_rules(self,item,origitem):
        if "f" in self.propRule and self.propRule["rule"]!="f":
            item=self.propRule["f"](item)
        if "mapping" in self.propRule and self.propRule["mapping"]:
            item=self.propRule[item]
        if "scaleby" in self.propRule:
            if self.propRule["scaleby"] in self.rules:
                item=item*self.propRule[self.get_by_rule(origitem,self.propRule["scaleby"])]
            else:
                item=item*self.propRule["scaleby"]
        if "colormap" in self.propRule:
            if matplotlib_loaded:
                item=matplotlib.cm.get_cmap(self.propRule["colormap"])(item)
            else:
                raise ImportError("The colormap feature uses matplotlib, and matplotlib cannot be imported.")
        return item

class LayerPropertyAssigner(PropertyAssigner):
    pass

class LayerColorAssigner(LayerPropertyAssigner):
    pass
class LayerAlphaAssigner(LayerPropertyAssigner):
    pass
class LayerLabelAssigner(LayerPropertyAssigner):
    pass
class LayerLabelLocAssigner(LayerPropertyAssigner):
    pass
class LayerOrderAssigner(LayerPropertyAssigner):
    pass
class LayerLabelSizeAssigner(LayerPropertyAssigner):
    pass
class LayerLabelColorAssigner(LayerPropertyAssigner):
    pass
class LayerLabelStyleAssigner(LayerPropertyAssigner):
    pass
class LayerLabelAlphaAssigner(LayerPropertyAssigner):
    pass


class NodePropertyAssigner(PropertyAssigner):
    rules=PropertyAssigner.rules.union(set(["degree","layer"]))
    def get_by_rule(self,item,rule):
        if rule=="degree":
            return self.net[item].deg()
        elif rule=="layer":
            return item[1] #assuming a single aspect here
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
    rules=NodePropertyAssigner.rules

class NodeSizeAssigner(NodePropertyAssigner):
    rules=NodePropertyAssigner.rules.union(set(["scaled"]))-set(["name"])
    def get_by_rule(self,item,rule):
        if rule=="scaled":
            coeff=self.propRule["scalecoeff"] if "scalecoeff" in self.propRule else 1.0
            n=len(self.net)     
            return coeff/float(math.sqrt(n))
        return super(NodeSizeAssigner,self).get_by_rule(item,rule)

    def apply_modify_rules(self,item,origitem):
        if "propscale" in self.propRule:
            coeff=self.propRule["propscale"]
            n=len(self.net)     
            item=item*coeff/float(math.sqrt(n))
        return super(NodeSizeAssigner,self).apply_modify_rules(item,origitem)


#nodes todo: marker

class EdgePropertyAssigner(PropertyAssigner):
    rules=PropertyAssigner.rules.union(set(["edgetype","edgeweight","sourcedestweight","layer"]))

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
        elif rule=="layer":
            if item[0][1]==item[1][1]:
                return item[0][1]
            else:
                return "interlayer"
        elif rule=="sourcedestweight":
            return item[0],item[1],self.net[item[0]][item[1]]
        return super(EdgePropertyAssigner,self).get_by_rule(item,rule)


class EdgeWidthAssigner(EdgePropertyAssigner):
    pass

class EdgeColorAssigner(EdgePropertyAssigner):
    pass

class EdgeStyleAssigner(EdgePropertyAssigner):
    pass

class EdgeAlphaAssigner(EdgePropertyAssigner):
    pass

class EdgeZAssigner(EdgePropertyAssigner):
    pass

