import pymnet

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
