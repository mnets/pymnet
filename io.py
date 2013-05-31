from net import MultisliceNetwork,CoupledMultiplexNetwork
import math

def read_ucinet(netinput):
    """Reads network in UCINET DL format.

    See http://www.analytictech.com/networks/dataentry.htm
    for informal definition of the format. This implemetation
    is based on the provided url and some example files at
    the UCINET website. There might be different versions of
    the file format?

    Parameters
    ----------
    netinput : The input file name if string, otherwise
               any iterable.

    Notes
    -----
    The labels are not case sensitive according to the example
    files. This function solves this problem by setting all the
    labels to lower case.

    """
    def read_labels(iterator,length):
        """Reads labels after label tag in the file.
        Labels can be separated with commas or line changes"""
        try:
            nlabels=0
            while nlabels<length:
                line=iterator.next()
                fields=line.split(",")
                for label in fields:
                    nlabels+=1
                    yield label.strip().lower()
        except StopIteration:
            raise Exception("File ended while reading labels.")

    #check if the input is file name instead of iterable
    if isinstance(netinput,str):
        netinput=open(netinput,'r')

    #create the input iterator
    ii=iter(netinput)

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
                raise Exception("Too many dimensions?")

            assert nchar.strip().lower()=="n"
            assert mchar.strip().lower()=="nm"

            assert nval.strip().isdigit()
            assert mval.strip().isdigit()
 
            return int(nval),int(mval)

        line=ii.next()
        assert line.lower().startswith("dl"), "File not starting with DL"
        if len(line[2:].strip())==0: #nothing more in this line
            line2=ii.next()
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
            line=ii.next().lstrip().lower()
            if line.startswith("format"):
                f=line.split("=")
                if len(f)==2:
                    format=f[1].strip()
                else:
                    raise Exception("Invalid line: %s"%line)
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
                raise Exception("Invalid command: %")%line
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
            clabels=range(n)
        else:
            clabels=labels

    #Next phase: read data
    
    #create the empty network
    if nm==1:
        net=MultisliceNetwork(dimensions=1)
    else:
        net=CoupledMultiplexNetwork(couplings=[("categorical",1.0)])

    if format=="fullmatrix" or "fullmatrix diagonal present":
        try:
            if labels_embedded: #first line is labels
                clabels=map(lambda x:x.lower(),ii.next().split())
                rlabels=[]
            assert len(clabels)==n,"Invalid number of labels."
            row=0
            while True:
                line=ii.next()
                if len(line.strip())!=0: #skip empty lines 
                    fields=line.split()
                    if labels_embedded:
                        rlabels.append(fields[0].lower())
                        fields=fields[1:]
                    assert len(fields)==n,"Invalid number of columns: %d"%len(fields)
                    for column,field in enumerate(fields):
                        if nm==1:
                            if clabels[column]!=rlabels[row]:
                                net[clabels[column]][rlabels[row]]=float(field)
                        else:
                            level=int(math.floor(row/n))
                            if clabels[column]!=rlabels[row%n]:
                                net[clabels[column],rlabels[row%n],llabels[level],llabels[level]]=float(field)
                    row+=1
        except StopIteration:
            assert row==n*nm, "Invalid number of rows in the data"
    else:
        raise Exception("Format '%s' is not supported" % format)

    return net
