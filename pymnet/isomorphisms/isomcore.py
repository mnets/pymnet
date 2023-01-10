

class AuxiliaryGraphBuilder(object):
    """This is a generic class for building auxiliary graphs. Backends can inherit this class to create auxiliary graph builders.
    """
    has_comparison=False #method can be used to compare networks
    has_complete_invariant=False #method can be used to create complete invariants
    has_automorphism_group_generators=False #method can be used to generate automorphism groups
    has_isomorphism_mapping=False #method can be used to generate an isomorphic mapping

    def __init__(self,net,allowed_aspects="all",reduction_type="auto"):
        assert net.directed == False, "Only undirected networks for now."
        self.net=net

        if allowed_aspects=="all":
            allowed_aspects=range(net.aspects+1)
        self.asp=sorted(allowed_aspects)
        self.nasp=list(filter(lambda a:a not in allowed_aspects,range(net.aspects+1)))

        self.nodemap={}
        self.auxnodemap={}
        self.colormap={}
        self.auxcolormap={}
                
        self.build_init()

        if reduction_type=="auto":
            self._build_graph_general() #this is the only one implemented so far
        elif reduction_type=="general":
            self._build_graph_general()
        else:
            raise Exception("Unknown reduction type: "+str(reduction_type))
            
        self.finalize()
            
    def _get_node_id(self,node):
        if node not in self.nodemap:
            assert len(self.auxnodemap)==0
            self.nodemap[node]=len(self.nodemap)            
        return self.nodemap[node]

    def _get_auxnode_id(self,auxnode):
        if auxnode not in self.auxnodemap:
            self.auxnodemap[auxnode]=len(self.nodemap)+len(self.auxnodemap)
        return self.auxnodemap[auxnode]
    
    def _slice_node_layer_allowed(self,nodelayer):
        s=[]
        for i in self.asp:
            s.append(nodelayer[i])
        return tuple(s)

    def _slice_node_layer_not_allowed(self,nodelayer):
        s=[]
        for i in self.nasp:
            s.append(nodelayer[i])
        return tuple(s)

    def _assert_full_order(self,seq):
        for i in range(len(seq)-1):
            assert seq[i]<seq[i+1], "Cannot sort the node or elementary layer names!"

    def _build_graph_general(self):
        """This is a reduction that works for all multilayer networks.
        """        

        #Find a canonical coloring scheme
        #Each node has a color that is determined by the non-mapped aspects
        nodecolors=set()
        for nl in self.net.iter_node_layers():
            nodecolors.add(self._slice_node_layer_not_allowed(nl))
        nodecolors_sorted=sorted(list(nodecolors))
        del nodecolors
        self._assert_full_order(nodecolors_sorted)
        self.colormap=dict( ((color,colorid) for colorid,color in enumerate(nodecolors_sorted) ))

        #each aux node has a color that is determined by the aspect
        self.auxcolormap=dict( ((auxcolor, auxcolorid+len(self.colormap)) for auxcolorid,auxcolor in enumerate(sorted(self.asp)) ) )


        #Add the underlying network
        #node-layers:
        for nl in self.net.iter_node_layers():
            nlid=self._get_node_id(nl)
            color=self._slice_node_layer_not_allowed(nl)
            colorid=self.colormap[color]
            self.add_node(nlid,colorid)

        #edges between node-layers:
        for nl1 in self.net.iter_node_layers():
            for nl2 in self.net[nl1]:
                nl1id=self._get_node_id(nl1)
                nl2id=self._get_node_id(nl2)
                self.add_link(nl1id,nl2id)


        #Add the auxiliary nodes and edges
        #add the aux nodes
        for a in self.asp:
            for elayer in self.net.slices[a]:
                auxid=self._get_auxnode_id( (a,elayer) )
                auxcolorid=self.auxcolormap[a]
                self.add_node(auxid,auxcolorid)
                
        #add the aux edges
        for nl in self.net.iter_node_layers():
            for a in self.asp:
                nlid=self._get_node_id(nl)
                auxid=self._get_auxnode_id( (a,nl[a]) )
                self.add_link(nlid,auxid)

    def compare_labels(self,other):
        assert self.auxcolormap==other.auxcolormap #this should be true if comparable
        return self.colormap==other.colormap


    def compare(self,other):
        #make sure that the two are comparable
        assert self.asp==other.asp and self.nasp==other.nasp, "Auxiliary graphs build for different isomorphisms, cannot compare."

        return self.compare_labels(other) and self.compare_structure(other)


    def complete_invariant_labels(self):
        # the colors for the colors for the nodes are determined in a way that there is canonical order for them
        # The self.colormap could be used directly for the invariant, but we want to make sure that the invariant
        # is valid even after it is serialized. To this end, we will sort the dict entries
        return tuple(sorted(self.colormap.items()))

    def get_complete_invariant(self):
        return (self.complete_invariant_labels(),self.complete_invariant_structure())

    def get_automorphism_generators(self,include_fixed=False):
        generators=[]
        #invauxnodemap=dict( ((v,k) for k,v in self.auxnodemap.iteritems() ) )
        invauxnodemap=dict( ((self.auxnodemap[k],k) for k in self.auxnodemap ) )
        for permutation in self._automorphism_generators():
            mperms=[]
            for a in range(self.net.aspects+1):
                mperms.append({})
            #for node,nodeid in self.auxnodemap.iteritems():
            for node in self.auxnodemap:
                nodeid=self.auxnodemap[node]
                aspect,elayer=node
                new_aspect,new_elayer=invauxnodemap[permutation[nodeid]]
                if elayer!=new_elayer or include_fixed:
                    mperms[aspect][elayer]=new_elayer
                assert aspect==new_aspect

            #add the aspects that are not permuted
            if include_fixed:
                for aspect in self.nasp:
                    for elayer in self.net.slices[aspect]:
                        mperms[aspect][elayer]=elayer

            generators.append(mperms)
        return generators

    def get_isomorphism(self,other,include_fixed=False):
        if self.compare(other):
            permutation=self._isomorphism_mapping(other)

            #The code is almost duplicate to the automorphisms
            #This should be cleaned up

            #invauxnodemap=dict( ((v,k) for k,v in other.auxnodemap.iteritems() ) )
            invauxnodemap=dict( ((other.auxnodemap[k],k) for k in other.auxnodemap ) )
            mperms=[]
            for a in range(self.net.aspects+1):
                mperms.append({})
            #for node,nodeid in self.auxnodemap.iteritems():
            for node in self.auxnodemap:
                nodeid=self.auxnodemap[node]
                aspect,elayer=node
                new_aspect,new_elayer=invauxnodemap[permutation[nodeid]]
                if elayer!=new_elayer or include_fixed:
                    mperms[aspect][elayer]=new_elayer
                assert aspect==new_aspect

            #add the aspects that are not permuted
            if include_fixed:
                for aspect in self.nasp:
                    for elayer in self.net.slices[aspect]:
                        mperms[aspect][elayer]=elayer            

            return mperms

        else:
            return None



    ## The following functions need to be overridden:
    def build_init(self):
        raise NotImplemented()

    def finalize(self):
        raise NotImplemented()        

    def add_node(self,name,color):
        raise NotImplemented()

    def add_link(self,node1,node2):
        raise NotImplemented()
    ##

    ## The following can be overridden if possible
    def compare_structure(self,other):
        raise NotImplemented()

    def complete_invariant_structure(self):
        raise NotImplemented()

    def _automorphism_generators(self):
        raise NotImplemented()

    def _isomorphism_mapping(self,other):
        raise NotImplemented()


    ##
