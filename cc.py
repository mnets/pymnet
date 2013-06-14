import itertools
from net import CoupledMultiplexNetwork

def cc(net,node,undefReturn=0.0):
    """Returns the clustering coefficient of a flat network.

    Complexity
    ----------
    Time complexity O(k^2), where k is the degree of the node. This 
    could be improved if it is known that the neighbors degrees are
    smaller than the nodes degrees to O(k*kn), where kn is the average 
    degree of all the neighbors. 

    Notices
    -------
    The function assumes that the network doesn't have any self-links,
    and that it's undirected.
    """
    degree=net[node].deg()
    if degree>=2:
        t=0
        for i,j in itertools.combinations(net[node],2):
            if net[i][j]!=net.noEdge:
                t+=1
        return 2*t/float(degree*(degree-1))
    else:
        return undefReturn

def cc_zhang(net,node,undefReturn=0.0):
    """
    References
    ----------
    B. Zhang and S. Horvath, Stat. App. Genet. Mol. Biol. 4, 17 (2005)
    """
    degree=net[node].deg()
    if degree>=2:
        nom,den=0,0
        for i,j in itertools.combinations(net[node],2):
            nij=net[node][i]*net[node][j]
            ij=net[i][j]
            den+=nij            
            if ij!=net.noEdge:
                nom+=nij*ij
        return nom/float(den)
    else:
        return undefReturn

def cc_onnela(net,node,undefReturn=0.0):
    """
    References
    ----------
    J.-P. Onnela, J. Saramaki, J. Kertesz, and K. Kaski, Phys. Rev. E 71, 065103 (2005)
    """
    degree=net[node].deg()
    if degree>=2:
        nom=0
        for i,j in itertools.combinations(net[node],2):
            ij=net[i][j]
            if ij!=net.noEdge:
                nom+=net[node][i]*net[node][j]*ij
        return 2*(nom)**(1/3.)/float(degree*(degree-1))
    else:
        return undefReturn

def cc_barrat(net,node,undefReturn=0.0):
    """
    References
    ----------
    A. Barrat, M. Barthelemy, R. Pastor-Satorras, and A. Vespignani, Proc. Natl. Acad. Sci. (USA) 101, 3747 (2004)
    """
    degree=net[node].deg()
    if degree>=2:
        nom=0
        for i,j in itertools.combinations(net[node],2):
            if net[i][j]!=net.noEdge:
                nom+=net[node][i]+net[node][j]
        return nom/float((degree-1)*net[node].str())
    else:
        return undefReturn


def cc_barrett(net,node,anet,undefReturn=0.0):
    """Multiplex clustering coefficient defined by Barrett et al.

    See SI of "Taking sociality seriously: the structure of multi-dimensional social networks as a source of information for individuals.", Louise Barrett, S. Peter Henzi, David Lusseau, Phil. Trans. R. Soc. B 5 August 2012 vol. 367 no. 1599 2108-2118

    \frac{\sum_j^n \sum_h^n \sum_k^b ( a_{ijk} \sum_l^b (a_{ihl} \sum_m^b a_{jhm} ) )} {\sum_j^n \sum_h^n \sum_k^b (a_{ijk} \sum_l^b \max(a_{ihl},a_{jhl}) )}
    """
    degree=anet[node].deg()
    if degree>=2:
        nom,den=0,0
        for i,j in itertools.combinations(anet[node],2):
            nij=anet[node][i]*anet[node][j]
            ij=anet[i][j]
            if ij!=anet.noEdge:
                nom+=nij*ij

        for j in anet[node]:
            for h in anet:
                m=0
                for layer in net.slices[1]:
                    m+=max(net[node,h,layer],net[j,h,layer])
                den+=anet[node,j]*m

        return 2*nom/float(den)
    else:
        return undefReturn

def cc_barrett_explicit(net,node,undefReturn=0.0):
    """Same as cc_barrett, but slower implementation.

    The Barrett cc is implemented here as it is written in the article
    without any optimizations. This function is here for validating
    the optimized version.
    """
    i=node
    n=list(net)
    b=net.slices[1]
    nom=0.0
    for j in n:
        for h in n:
            for k in b:
                t1=0.0
                for l in b:
                    t2=0.0
                    for m in b:
                        t2+=net[j,h,m]
                    t1+=t2*net[i,h,l]
                nom+=net[i,j,k]*t1

    den=0.0
    for j in n:
        for h in n:
            for k in b:
                t1=0.0
                for l in b:
                    t1+=max(net[i,h,l],net[j,h,l])
                den+=net[i,j,k]*t1

    return nom/float(den)


def cc_sequence(net,node):
    """Returns number of triangles and connected tuples around the node for each layer.
    """
    triangles,tuples=[],[]
    for layer in net.A:
        intranet=net.A[layer]
        t=0
        degree=intranet[node].deg()
        if degree>=2:
            for i,j in itertools.combinations(intranet[node],2):
                if intranet[i][j]!=intranet.noEdge:
                    t+=1
        triangles.append(t)
        tuples.append((degree*(degree-1))/2)
    return triangles,tuples


def cc_layers_avg(net,node):
    #how to handle undefined cc?
    nom,den=cc_sequence(net,node)
    tot=map(lambda x,y:x/float(y),nom,den)
    return sum(tot)/float(len(tot))

def cc_layers_wavg(net,node):

    nom,den=cc_sequence(net,node)
    return sum(nom)/float(sum(den))

def cc_cycle_vector_bf(net,node,layer,undefReturn=0.0):
    """Counts all the cycles.

    Brute force implementation.
    """
    assert isinstance(net,CoupledMultiplexNetwork)
    assert net.dimensions==2
    
    aaa=0
    aacac=0 # == cacaa
    acaac=0 # == caaca
    acaca=0
    acacac=0

    intranet=net.A[layer]
    degree=intranet[node].deg()
    other_layers=map(lambda x:x[1],net[node,node,layer,:])

    #aaa
    if degree>=2:
        for i,j in itertools.combinations(intranet[node],2):
            if intranet[i][j]!=intranet.noEdge:
                aaa+=1    
    aaa=aaa*2

    #aacac
    for i in intranet[node]:
        for j in intranet[i]:
            for layer2 in other_layers:
                if net[j,layer2][node,layer2]!=net.noEdge:
                    aacac+=1

    #acaac
    for i in intranet[node]:
        for layer2 in other_layers:
            for j,dummy in net[i,:,layer2,layer2]:
                if net[j,layer2][node,layer2]!=net.noEdge:
                    acaac+=1

    #acaca
    if degree>=2:
        for i,j in itertools.combinations(intranet[node],2):
            for layer2 in other_layers:
                if net[i,layer2][j,layer2]!=net.noEdge:
                    acaca+=1
    acaca=acaca*2

    #acacac
    for i in intranet[node]:
        for layer2 in other_layers:
            for j,dummy in net[i,:,layer2,layer2]:
                for layer3 in other_layers:
                    if layer3!=layer2:
                        if net[j,layer3][node,layer3]!=net.noEdge:
                            acacac+=1
    
    return aaa,aacac,acaac,acaca,acacac

def cc_cycle_vector_adj(net,node,layer):
    import numpy
    adj,nodes1=net.get_supra_adjacency_matrix()

    temp=net.couplings[0]
    net.couplings[0]=('categorical',0)
    a,nodes2=net.get_supra_adjacency_matrix()
    net.couplings[0]=temp

    assert nodes1==nodes2

    c=adj-a

    ch=c+numpy.eye(len(c))

    node=node+layer*len(net)
    aaa=(a*a*a)[node,node]
    aacac=(a*a*c*a*c)[node,node]
    acaac=(a*c*a*a*c)[node,node]
    acaca=(a*c*a*c*a)[node,node]
    acacac=(a*c*a*c*a*c)[node,node]

    cacaa=(c*a*c*a*a)[node,node]
    caaca=(c*a*a*c*a)[node,node]
    cacaca=(c*a*c*a*c*a)[node,node]

    assert aacac==cacaa
    assert acaac==caaca
    assert acacac==cacaca

    ach3=(a*ch*a*ch*a*ch)[node,node]
    assert aaa+aacac+acaac+acaca+acacac==ach3

    return aaa,aacac,acaac,acaca,acacac

def cc_5cycles(net,node,anet,undefReturn=0.0):
    nom,den=0,0
    #First calculate cc inside the layers
    tr,tu=cc_sequence(net,node)
    tr_intra=sum(tr)
    tu_intra=sum(tu)

    #Then go through the cases where node is central
    tr_central=0
    tu_central=0
    for layer in net.A:
        intranet=net.A[layer]
        t=0
        degree=intranet[node].deg()
        if degree>=2:
            for i,j in itertools.combinations(intranet[node],2):
                for layer2 in net[node,node,layer,:]:
                    if net[i,layer2][j,layer2]!=net.noEdge:
                        t+=1
        tr_central+=t
        tu_central+=(len(net.layers)-1)*((degree*(degree-1))/2)
   
    #Last, go through cases where node is not central
    #to be done
