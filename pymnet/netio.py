"""Functions for reading and writing networks in different file formats.
"""
from .net import MultilayerNetwork,MultiplexNetwork
import math,json,os

def write_ucinet(net,outputfile,outputType="edges"):
    assert isinstance(net,MultiplexNetwork), "Multilayer networks not supported by the UCINET file format."
    if isinstance(outputfile,"".__class__) or isinstance(outputfile,u"".__class__):
        outputfile=open(outputfile,'w')
    
def write_json(net,outputfile=None):
    """Writes a multiplex network with a single aspect in a JSON format.
    """
    assert isinstance(net,MultiplexNetwork)
    assert net.aspects==0 or net.aspects==1
    nets={}
    node2index={}
    nets["nodes"]=[]    
    for i,node in enumerate(net):
        nets["nodes"].append({"name":node})
        node2index[node]=i

    layer2index={}
    nets["layers"]=[]    
    for i,layer in enumerate(net.get_layers()):
        nets["layers"].append({"name":layer})
        layer2index[layer]=i

    nets["links"]=[]
    for layer in net.get_layers():
        for edge in net.A[layer].edges:
            nets["links"].append({"source":node2index[edge[0]],
                                  "target":node2index[edge[1]],
                                  "value" :edge[2],
                                  "layer" :layer2index[layer]})

    if outputfile!=None:
        if isinstance(outputfile,"".__class__) or isinstance(outputfile,u"".__class__):
            outputfile=open(outputfile,'w')

        json.dump(nets,outputfile)
        outputfile.close()
    else:
        return json.dumps(nets)

def read_edge_files(edgeinput,layerinput=None,nodeinput=None,couplings='categorical',fullyInterconnected=True,directed=False,ignoreSelfLink=True):
    """A multiplex file separated into files for layers, edge and nodes.
    """
    net=MultiplexNetwork(couplings=[couplings],fullyInterconnected=fullyInterconnected,directed=directed)
    layerfile=open(layerinput,'r') if isinstance(layerinput,str) else layerinput
    edgefile=open(edgeinput,'r') if isinstance(edgeinput,str) else edgeinput
    nodefile=open(nodeinput,'r') if isinstance(nodeinput,str) else nodeinput

    for line in edgefile:
        li,fi,ti,w=line.split()
        li,fi,ti,w=int(li),int(fi),int(ti),float(w)
        if fi!=ti or not ignoreSelfLink:
            net[fi,ti,li]=w
    return net



def write_edge_files(net,outputfiles,columnSeparator="\t",rowSeparator="\n",weights=True,masterFile=False,numericNodes=False):
    assert isinstance(net,MultiplexNetwork)
    assert net.aspects==1
    if masterFile:
        mofile=open(outputfiles+".txt",'w')

    if numericNodes:
        nodetonumber={}
        for i,node in enumerate(net):
            nodetonumber[node]=i

    for layer in net.get_layers():
        ofilename=outputfiles+str(layer)+".edg"
        ofile=open(ofilename,'w')
        if masterFile:
            mofile.write(os.path.basename(ofilename)+";"+str(layer)+";\n")
        for edge in net.A[layer].edges:
            n1,n2=edge[0],edge[1]
            if numericNodes:
                n1,n2=nodetonumber[n1],nodetonumber[n2]
            if weights:
                ofile.write(str(n1)+columnSeparator+str(n2)+columnSeparator+str(edge[2])+rowSeparator)
            else:
                ofile.write(str(n1)+columnSeparator+str(n2)+rowSeparator)
        ofile.close()
    if masterFile:
        mofile.close()

def read_ucinet(netinput,couplings=('categorical',1.0),fullyInterconnected=True):
    """Reads network in UCINET DL format.

    See http://www.analytictech.com/networks/dataentry.htm
    for informal definition of the format. This implementation
    is based on the provided url and some example files at
    the UCINET website.

    Parameters
    ----------
    netinput : string, sequence
       The input file name if string, otherwise any iterable.
    couplings : tuple
       Passed for MultiplexNetwork when the network object is created.
    fullyInterconnected : bool 
        If False, nodes having zero degree on a layer are not added 
        to that layer.
               
    Notes
    -----
    The labels are not case sensitive according to the example
    files. This function solves this problem by setting all the
    labels to lower case.

    Currently, the network is assumed to be unweighted, and if
    the input file contains a directed network the an undirected
    network is returned anyway. The directions are removed in a
    way that i and j are connected if there is either link 
    i->j or j->i (or both).
    """

    def read_labels(iterator,length):
        """Reads labels after label tag in the file.
        Labels can be separated with commas or line changes"""
        try:
            nlabels=0
            while nlabels<length:
                #line=iterator.next()
                line=iterator.send(None)
                fields=line.split(",")
                for label in fields:
                    nlabels+=1
                    yield label.strip()#.lower()
        except StopIteration:
            raise Exception("File ended while reading labels.")

    #check if the input is file name instead of iterable
    if isinstance(netinput,str):
        netinput=open(netinput,'r')

    #create the input iterator
    #ii=iter(netinput)
    ii=(x for x in netinput)

    #The file should start with dl or DL.
    #Then on the same row or next row it should contain
    #the number of nodes and layers (if multiplex)
    #E.g 'DL N = 10 NM = 2' or 'DL\nN = 10 NM = 2'
    try:
        def parse_size(line):
            dims=len(line.split("="))-1
            if dims==1:
                nchar,nval=line.split("=")
                mchar,mval="nm","1"
            elif dims==2:
                nchar,nvalmchar,mval=line.split("=")
                try:
                    nval,mchar=nvalmchar.split() #any whitespace ok
                except ValueError:
                    raise Exception("Error reading number of nodes in line: %s"%line)
            elif dims==0:
                raise Exception("Number of nodes (and slices) not given")
            else:
                raise Exception("Too many aspects?")

            assert nchar.strip().lower()=="n"
            assert mchar.strip().lower()=="nm"

            assert nval.strip().isdigit()
            assert mval.strip().isdigit()
 
            return int(nval),int(mval)

        #line=ii.next()
        line=ii.send(None)
        assert line.lower().startswith("dl"), "File not starting with DL"
        if len(line[2:].strip())==0: #nothing more in this line
            #line2=ii.next()
            line2=ii.send(None)
            n,nm=parse_size(line2)
        else: #the size is on this line
            n,nm=parse_size(line[2:])
    except StopIteration:
        raise Exception("Empty or incomplete file.")
    
    #Lets read the rest of the variables next.
    #default values:
    format="fullmatrix"
    labels=None
    rlabels=None
    clabels=None  
    llabels=None
    labels_embedded=False
    data=False
    try:
        while True:
            #line=ii.next().lstrip().lower()
            line=ii.send(None).lstrip().lower()
            if line.startswith("format"):
                f=line.split("=")
                if len(f)==2:
                    format=f[1].strip()
                else:
                    raise Exception("Invalid line: '%s'"%line.strip())
            elif line.startswith("labels:"):
                labels=list(read_labels(ii,n))
            elif line.startswith("row labels:"):
                rlabels=list(read_labels(ii,n))
            elif line.startswith("column labels:"):
                clabels=list(read_labels(ii,n))
            elif line.startswith("level labels:"):
                llabels=list(read_labels(ii,nm))
            elif line.startswith("data"):
                data=True
                raise StopIteration
            elif line.startswith("labels embedded"):
                labels_embedded=True
            else:
                raise Exception("Invalid command: '%s'"%line.strip())
    except StopIteration:
        pass
    if data==False:
        raise Exception("No data found.")

    #sort out the labels
    if labels_embedded and (labels!=None or rlabels!=None or clabels!=None):
        raise Exception("No additional labels when using embedded labels.")
    if llabels==None:
        llabels=range(nm)
    if labels!=None and rlabels!=None and clabels!=None:
        raise Exception("Redundant labels given.")
    if rlabels==None:
        if labels==None:
            rlabels=range(n)
        else:
            rlabels=labels
    if clabels==None:
        if labels==None:
            clabels=list(range(n))
        else:
            clabels=labels

    #Next phase: read data
    
    #create the empty network
    if nm==1:
        net=MultilayerNetwork(aspects=0)
    else:
        net=MultiplexNetwork(couplings=[couplings],fullyInterconnected=fullyInterconnected)

    if format=="fullmatrix" or "fullmatrix diagonal present":
        try:
            if labels_embedded: #first line is labels
                #clabels=map(lambda x:x.lower(),ii.next().split())
                clabels=list(map(lambda x:x.lower(),ii.send(None).split()))
                rlabels=[]
            assert len(clabels)==n,"Invalid number of labels."
            row=0
            while True:
                #line=ii.next().strip()
                line=ii.send(None).strip()
                fields=line.split()
                while len(fields)<n:
                    #line=ii.next().strip()
                    line=ii.send(None).strip()
                    fields.extend(line.split())

                if labels_embedded:
                    rlabels.append(fields[0].lower())
                    fields=fields[1:]
                assert len(fields)==n,"Invalid number of columns: %d"%len(fields)
                for column,field in enumerate(fields):
                    if nm==1:
                        if clabels[column]!=rlabels[row]:
                            if float(field)!=0.0:
                                net[clabels[column]][rlabels[row]]=float(field)
                    else:
                        level=int(math.floor(row/n))
                        if clabels[column]!=rlabels[row%n]:
                            if float(field)!=0.0:
                                net[clabels[column],rlabels[row%n],llabels[level],llabels[level]]=float(field)
                row+=1
        except StopIteration:
            assert row==n*nm, "Invalid number of rows in the data"
    else:
        raise Exception("Format '%s' is not supported" % format)


    if fullyInterconnected and nm!=1:
        for layer in llabels:
            for node in clabels:
                net.A[layer].add_node(node)
            for node in rlabels:
                net.A[layer].add_node(node)

    return net
