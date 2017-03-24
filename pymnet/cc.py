"""Clustering coefficients in multiplex networks.
"""

import itertools
from .net import MultiplexNetwork
from . import transforms

def cc_num_den(net,node):
    degree=net[node].deg()
    t=0
    for i,j in itertools.combinations(net[node],2):
        if net[i][j]!=net.noEdge:
            t+=1
    return t,(degree*(degree-1))/2

def lcc(net,node,undefReturn=0.0):
    """The local clustering coefficient of a node in monoplex network.

    Parameters
    ----------
    net : MultilayerNetwork with aspects=0
       The input network.
    node : any object
       The focal node. Given as the node index in the network.
    undefReturn : any object
       Value of this parameter is returned if the clustering coefficient is not defined.

    Returns
    -------
    float or object
       The clustering coefficient value, or the undefReturn value if the clustering
       coefficient is not defined for the node.

    Notes
    -----
    Time complexity O(k^2), where k is the degree of the node. This 
    could be improved if it is known that the neighbors degrees are
    smaller than the nodes degrees to O(k*kn), where kn is the average 
    degree of all the neighbors. 

    The function assumes that the network doesn't have any self-links,
    and that it's undirected.
    """
    degree=net[node].deg()
    if degree>=2:
        num,den=cc_num_den(net,node)
        return num/float(den)
    else:
        return undefReturn


def cc_zhang(net,node,undefReturn=0.0):
    r"""Zhang's local clustering coefficient of a node in weighted monoplex network.

    The clustering coefficient for node i is given by formula:

    .. math:: c_{Z,i} = \frac{\sum_{j,h} W_{ij}W_{ih}W_{jh}}{ w_{\max}\sum_{j \neq h} W_{ij}W_{ih}}=\frac{(W^3)_{ii}}{((W(w_{\max}F)W)_{ii}}


    References
    ----------
    B. Zhang and S. Horvath, Stat. App. Genet. Mol. Biol. 4, 17 (2005)

    See also
    --------
    gcc_zhang : The global version of the clustering coefficient

    """
    maxw=max(map(lambda x:x[2],net.edges))
    degree=net[node].deg()
    if degree>=2:
        nom,den=0,0
        for i,j in itertools.combinations(net[node],2):
            nij=net[node][i]*net[node][j]
            ij=net[i][j]
            den+=nij            
            if ij!=net.noEdge:
                nom+=nij*ij
        return nom/float(den)/float(maxw)
    else:
        return undefReturn

def gcc_zhang(net):
    r"""Global version of the Zhang's clustering coefficient of a node in weighted monoplex network.

    The clustering coefficient is given by formula:

    .. math:: c_Z = \frac{\sum_{i,j,h} W_{ij}W_{ih}W_{jh}}{ w_{\max}\sum_i \sum_{j \neq h} W_{ij}W_{ih}}

    See also
    --------
    cc_zhang : The local version of the clustering coefficient

    """

    maxw=max(map(lambda x:x[2],net.edges))
    nom,den=0,0
    for node in net:
        degree=net[node].deg()
        if degree>=2:
            for i,j in itertools.combinations(net[node],2):
                nij=net[node][i]*net[node][j]
                ij=net[i][j]
                den+=nij            
                if ij!=net.noEdge:
                    nom+=nij*ij
    if den!=0:
        return nom/float(den)/float(maxw)
    else:
        return None


def cc_onnela(net,node,undefReturn=0.0):
    r"""Onnela's local clustering coefficient of a node in weighted monoplex network.

    The clustering coefficient for node i is given by formula:

    .. math:: c_{O,i} = \frac{1}{w_{\max}k_{i}(k_{i}-1)} \sum_{j,h} (W_{ij}W_{ih}W_{jh})^{1/3}

    References
    ----------
    J.-P. Onnela, J. Saramaki, J. Kertesz, and K. Kaski, Phys. Rev. E 71, 065103 (2005)
    """
    maxw=max(map(lambda x:x[2],net.edges))
    degree=net[node].deg()
    if degree>=2:
        nom=0
        for i,j in itertools.combinations(net[node],2):
            ij=net[i][j]
            if ij!=net.noEdge:
                nom+=(net[node][i]*net[node][j]*ij)**(1./3.)
        return 2*nom/float(degree*(degree-1))/float(maxw)
    else:
        return undefReturn

def cc_barrat(net,node,undefReturn=0.0):
    r"""Barrat's local clustering coefficient of a node in weighted monoplex network.

    The clustering coefficient for node i is given by formula:

    .. math:: c_{Ba,i} = \frac{1}{s_{i}(k_{i}-1)}\sum_{j,h}\frac{(W_{ij}+W_{ih})}{2} A_{ij}A_{ih}A_{jh}

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

def cc_barrett_optimized(net,node,anet,undefReturn=0.0):
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

        ineighs=set(anet[node])
        for j in anet[node]:
            jneighs=set(anet[j])
            for h in ineighs | jneighs:
                m=0
                if net.fullyInterconnected:
                    layers=net.slices[1]
                else:
                    layers=net._nodeToLayers[h] #itertools.imap(lambda x:x[0],net._nodeToLayers[h])
                for layer in layers:
                    m+=max(net[node,h,layer],net[j,h,layer])
                den+=anet[node,j]*m

        if den!=0.0:
            return 2*nom/float(den)
        else:
            return undefReturn
    else:
        return undefReturn

def cc_barrett(net,node,anet,undefReturn=0.0):
    r"""Barrett's local clustering coefficient of a node in multiplex network.

    The clustering coefficient for node i is given by formula:

    .. math:: c_{Be,i} = \frac{\sum_j^n \sum_h^n \sum_k^b ( A_{ijk} \sum_l^b (A_{ihl} \sum_m^b A_{jhm} ) )} {\sum_j^n \sum_h^n \sum_k^b (A_{ijk} \sum_l^b \max(A_{ihl},A_{jhl}) )}

    References
    ----------
    See SI of "Taking sociality seriously: the structure of multi-dimensional social networks as a source of information for individuals.", Louise Barrett, S. Peter Henzi, David Lusseau, Phil. Trans. R. Soc. B 5 August 2012 vol. 367 no. 1599 2108-2118
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

        if den!=0.0:
            return 2*nom/float(den)
        else:
            return undefReturn
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

    if den==0.0:
        return undefReturn
    else:
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

def gcc_super_graph_no_couplings(net):
    snum,sden=0,0
    for node in net.slices[0]:
        t,d=cc_sequence(net,node)
        snum+=sum(t)
        sden+=sum(d)
    if sden!=0:
        return snum/float(sden)
    else:
        return None

def gcc_super_graph(net):
    snum,sden=0,0
    for node in itertools.product(*net.slices):
        num,den=cc_num_den(net,node)
        snum+=num
        sden+=den
    if sden!=0:
        return snum/float(sden)
    else:
        return None

def elementary_cycles(net,node=None,layer=None,anet=None):
    """Returns the elementary 3-cycle counts in a multiplex network.

    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    node : any object
       The focal node. Given as node index in the network.
    layer : any object
       The focal layer. Given as layer index in the network.

    Returns
    -------
    cycles : tuple
        Returns the elementary cycles around the node-layer pair in the
        following order:
        aaa,aacac,acaac,acaca,acacac,afa,afcac,acfac,acfca,acfcac
    
    References
    ----------
    "Clustering Coefficients in Multiplex Networks", E. Cozzo et al. , arXiv:1307.6780 [physics.soc-ph]

    """
    if node!=None and layer!=None:
        return cc_cycle_vector_bf(net,node,layer)
    sums=[0 for i in range(10)]
    nodes=list(net) if node==None else [node]
    if net.fullyInterconnected and (anet!=None or node==None):
        if anet==None:
            anet=transforms.aggregate(net,1)
        for n in nodes:
            sums=map(lambda x,y:x+y,sums,cc_cycle_vector_anet(net,n,layer=layer,anet=anet))
    else:
        layers=net.iter_layers() if layer==None else [layer]
        for l in layers:
            for n in nodes:
                sums=map(lambda x,y:x+y,sums,cc_cycle_vector_bf(net,n,l))
    return tuple(sums)


def cc_cycle_vector_bf(net,node,layer,undefReturn=0.0):
    """Counts all the cycles.

    Brute force implementation.
    """
    assert isinstance(net,MultiplexNetwork)
    assert net.aspects==1
    
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
            #for layer2 in other_layers:
            for dummy,layer2 in net[j,j,layer,:]:
                if net[j,layer2][node,layer2]!=net.noEdge:
                    aacac+=1

    #acaac
    for i in intranet[node]:
        #for layer2 in other_layers:
        for dummy,layer2 in net[i,i,layer,:]:
            for j,dummy in net[i,:,layer2,layer2]:
                if net[j,layer2][node,layer2]!=net.noEdge:
                    acaac+=1

    #acaca
    if degree>=2:
        for i,j in itertools.combinations(intranet[node],2):
            #for layer2 in other_layers:
            for dummy,layer2 in net[i,i,layer,:]:
                if net[i,layer2][j,layer2]!=net.noEdge:
                    acaca+=1
    acaca=acaca*2

    #acacac
    for i in intranet[node]:
        #for layer2 in other_layers:
        for dummy,layer2 in net[i,i,layer,:]:
            for j,dummy in net[i,:,layer2,layer2]:
                #for layer3 in other_layers:
                for dummy,layer3 in net[j,j,layer2,:]:
                    if layer3!=layer:
                        if net[j,layer3][node,layer3]!=net.noEdge:
                            #print node,",",layer,"-",i,",",layer2,"-",j,",",layer3
                            #print j,node,layer3,net[j,layer3][node,layer3]
                            #print i,node,layer,net[i,layer][node,layer]
                            #print i,j,layer2,net[i,layer2][j,layer2]
                            acacac+=1


    #afa
    afa=(intranet[node].deg()*(intranet[node].deg()-1))

    afcac=0
    neighbors=set(intranet[node])
    for dummy,layer2 in net[node,node,layer,:]:
        for i,dummy in net[node,:,layer2,layer2]:
            if net[i,i,layer,layer2]!=net.noEdge:
                if i in neighbors:
                    afcac+=len(neighbors)-1
                else:
                    afcac+=len(neighbors)

    if net.fullyInterconnected:
        acfca=afa*(len(net.slices[1])-1)        
        #afcac,acfac
        #afcac=0 
        #for i in intranet[node]:
        #    for layer2 in other_layers:
        #        for j,dummy in net[node,:,layer2,layer2]:
        #            if i!=j:
        #                afcac+=1
        acfac=afcac
        acfcac=afcac*(len(net.slices[1])-2)
    else:
        acfac=0 
        for i in intranet[node]:
            for dummy,layer2 in net[i,i,layer,:]:
                if net[node,node,layer,layer2]!=net.noEdge:
                    if net[node,i,layer2,layer2]:
                        acfac+=net[node,:,layer2,layer2].deg()-1
                    else:
                        acfac+=net[node,:,layer2,layer2].deg()

        acfca=0 
        layertonode={}
        for i in intranet[node]:
            for dummy,layer2 in net[i,i,layer,:]:
                if layer2 not in layertonode:
                    layertonode[layer2]=set()
                layertonode[layer2].add(i)
        #if intranet[node].deg()>0:
        #   assert len(layertonode)==(len(net.slices[1])-1),(len(layertonode),(len(net.slices[1])-1))
        for nodelist in layertonode.values():
            #assert len(nodelist)==intranet[node].deg(),(len(nodelist),intranet[node].deg())
            acfca+=(len(nodelist)*(len(nodelist)-1))
    
        #raise NotImplemented()
        acfcac=0
        for i in intranet[node]:
            for dummy,layer3 in net[node,node,layer,:]:
                for j,dummy in net[node,:,layer3,layer3]:
                    if i!=j:
                        if net[i,i,layer,:].deg()>net[j,j,layer3,:].deg():
                            for dummy,layer2 in net[j,j,layer3,:]:
                                if layer2!=layer:
                                    if net[i,i,layer,layer2]!=net.noEdge:
                                        acfcac+=1
                        else:
                            for dummy,layer2 in net[i,i,layer,:]:
                                if layer2!=layer3:
                                    if net[j,j,layer3,layer2]!=net.noEdge:
                                        acfcac+=1


    return aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac


def cc_cycle_vector_anet(net,node,layer=None,anet=None,undefReturn=0.0):
    """Counts all the cycles.

    Optimized using aggregated network. Works only for a fully-interconnected
    networks.

    If layer is None then the cycle vectors are calculate as sums over all
    node-layer pairs. In this case the computational complexity is O(b*k^2).
    """
    assert isinstance(net,MultiplexNetwork)
    assert net.aspects==1
    assert net.fullyInterconnected

    aaa=0
    aacac=0 # == cacaa
    acaac=0 # == caaca
    acaca=0
    acacac=0

    if layer!=None:
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
                aacac+=int(anet[j,node])
                if net[j,node,layer]!=net.noEdge:
                    aacac+= -1

        #acaac
        for i in intranet[node]:
            for dummy,layer2 in net[i,i,layer,:]:
                for j,dummy in net[i,:,layer2,layer2]:
                    if net[j,layer2][node,layer2]!=net.noEdge:
                        acaac+=1

        #acaca
        if degree>=2:
            for i,j in itertools.combinations(intranet[node],2):
                acaca+=int(anet[i,j])
                if net[i,j,layer]!=net.noEdge:
                    acaca+= -1            
        acaca=acaca*2

        #acacac
        for i in intranet[node]:
            for dummy,layer2 in net[i,i,layer,:]:
                for j,dummy in net[i,:,layer2,layer2]:
                    acacac+=int(anet[j,node])
                    if net[j,node,layer]!=net.noEdge:
                        acacac+= -1
                    if net[j,node,layer2]!=net.noEdge:
                        acacac+= -1


        #afa
        afa=(intranet[node].deg()*(intranet[node].deg()-1))

        afcac=0
        neighbors=set(intranet[node])
        for i in anet[node]:
            ledges=int(anet[i,node])-1 if net[i,node,layer]!=net.noEdge else int(anet[i,node])
            if i in neighbors:
                afcac+=(len(neighbors)-1)*ledges
            else:
                afcac+=len(neighbors)*ledges

        acfca=afa*(len(net.slices[1])-1)        
        acfac=afcac
        acfcac=afcac*(len(net.slices[1])-2)
    else:
        #aaa
        for layer in net.iter_layers():
            if net.A[layer][node].deg()>=2:
                for i,j in itertools.combinations(net.A[layer][node],2):
                    if net.A[layer][i][j]!=net.noEdge:
                        aaa+=1    
        aaa=aaa*2

        #aacac
        for layer in net.iter_layers():
            for i in net.A[layer][node]:
                for j in net.A[layer][i]:
                    aacac+=int(anet[j,node])
                    if net[j,node,layer]!=net.noEdge:
                        aacac+= -1

        #acaac
        acaac=aacac

        #acaca
        for layer in net.iter_layers():
            if net.A[layer][node].deg()>=2:
                for i,j in itertools.combinations(net.A[layer][node],2):
                    acaca+=int(anet[i,j])
                    if net[i,j,layer]!=net.noEdge:
                        acaca+= -1            
        acaca=acaca*2

        #acacac
        tot=0
        if anet[node].deg()>=2:
            for i,j in itertools.combinations(anet[node],2):
                    if anet[i,j]!=net.noEdge:
                        tot+=int(anet[node,i])*int(anet[i,j])*int(anet[j,node])
        acacac=2*tot-aaa-aacac-acaac-acaca

        #afa
        afa=0
        for layer in net.iter_layers():
            afa+=(net.A[layer][node].deg()*(net.A[layer][node].deg()-1))

        afcac=0
        for layer in net.iter_layers():
            neighbors=set(net.A[layer][node])
            for i in anet[node]:
                ledges=int(anet[i,node])-1 if net[i,node,layer]!=net.noEdge else int(anet[i,node])
                if i in neighbors:
                    afcac+=(len(neighbors)-1)*ledges
                else:
                    afcac+=len(neighbors)*ledges

        acfca=afa*(len(net.slices[1])-1)       
        acfac=afcac
        acfcac=afcac*(len(net.slices[1])-2)
        

    return aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac



def cc_cycle_vector_adj(net,node,layer):
    import numpy
    adj,nodes1=net.get_supra_adjacency_matrix()

    temp=net.couplings[0]
    net.couplings[0]=('categorical',0)
    a,nodes2=net.get_supra_adjacency_matrix()
    net.couplings[0]=temp

    a_test,nodes3=net.get_supra_adjacency_matrix(includeCouplings=False)
    assert (a==a_test).all()

    assert nodes1==nodes2

    c=adj-a

    ch=c+numpy.eye(len(c))

    node=nodes1.index( (node,layer) )
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

    fn=get_full_multiplex_network(net.slices[0],net.slices[1])
    f,node3=fn.get_supra_adjacency_matrix(includeCouplings=False)
    afa=(a*f*a)[node,node]
    afcac=(a*f*c*a*c)[node,node]
    acfac=(a*c*f*a*c)[node,node]
    acfca=(a*c*f*c*a)[node,node]
    acfcac=(a*c*f*c*a*c)[node,node]


    b=len(net.slices[1])
    if net.fullyInterconnected:
        assert afcac==acfac
        assert (b-1)*afa==acfca
        assert acfcac==(b-2)*afcac

    return aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac

def gcc_aw_vector_adj(net):
    def get_nom_den(p,ph):
        nom=[]
        for i in range(len(p)):
            nom.append(p[i,i])

        den=[]
        for i in range(len(p)):
            den.append(ph[i,i])
        return nom,den

    import numpy
    adj,nodes1=net.get_supra_adjacency_matrix()    
    a,nodes2=net.get_supra_adjacency_matrix(includeCouplings=False)
    c=adj-a

    fn=get_full_multiplex_network(net.slices[0],net.slices[1])
    f,node3=fn.get_supra_adjacency_matrix(includeCouplings=False)

    aaa=a*a*a
    afa=a*f*a
    c1_nom,c1_den=get_nom_den(aaa,afa)

    p21=a*a*c*a*c + a*c*a*a*c + a*c*a*c*a
    ph21=a*f*c*a*c + a*c*f*a*c + a*c*f*c*a
    c2_nom,c2_den=get_nom_den(p21,ph21)
    #assert (a*f*c*a*c)[1,1]==(a*c*f*a*c)[1,1]
    #assert (a*c*f*c*a)[1,1]==(a*f*a)[1,1]*(len(net.slices[1])-1)
    #assert (a*f*c*a*c)[1,1]*(len(net.slices[1])-2)==(a*c*f*c*a*c)[1,1]
    #assert (f*c==c*f).all()

    p111=a*c*a*c*a*c
    ph111=a*c*f*c*a*c
    c3_nom,c3_den=get_nom_den(p111,ph111)

    return c1_nom,c1_den,c2_nom,c2_den,c3_nom,c3_den

def cc_aw_vector(net):
    c1_nom,c1_den,c2_nom,c2_den,c3_nom,c3_den=[],[],[],[],[],[]
    for node in net:
        for layer in net.get_layers(1):
            aaa,aacac,acaac,acaca,acacac,afa,afcac,acfac,acfca,acfcac=elementary_cycles(net,node,layer)
            c1_nom.append(aaa)
            c1_den.append(afa)
            c2_nom.append(aacac+acaac+acaca)
            c2_den.append(afcac+acfac+acfca)
            c3_nom.append(acacac)
            c3_den.append(acfcac)
    return c1_nom,c1_den,c2_nom,c2_den,c3_nom,c3_den


def gcc_aw_seplayers_adj(net,w1=1./3.,w2=1./3.,w3=1./3.,returnCVector=False):
    c1_nom,c1_den,c2_nom,c2_den,c3_nom,c3_den=gcc_aw_vector_adj(net)
    if sum(c1_den)!=0:
        c1=sum(c1_nom)/float(sum(c1_den))
    else:
        c1=0
    if sum(c2_den)!=0:
        c2=sum(c2_nom)/float(sum(c2_den))
    else:
        c2=0
    if len(net.slices[1])==2:
        return w1*c1+w2*c2
    if sum(c3_den)!=0:
        c3=sum(c3_nom)/float(sum(c3_den))
    else:
        c3=0

    if returnCVector:
        return c1,c2,c3

    return w1*c1+w2*c2+w3*c3



def lcc_aw(net,node,layer,w1=1./2.,w2=1./2.,w3=None,returnCVector=False,anet=None):
    r"""The local version of the alternating walker clustering coefficient for multiplex networks.

    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    node : any object
       The focal node. Given as node index in the network.
    layer : any object
       The focal layer. Given as layer index in the network.
    w1,w2,w3 : weights of the contributions of different layers.
       If w3 is set to None then w1 and w2 correspond to the "costs" of staying at a layer and
       changing the layer, i.e. w1 = :math:`\beta` and w2 = :math:`\gamma`
    returnCVector : bool
       If True, returns a vector containing the three different local clustering coefficients
       :math:`c_1,c_2,c_3`. Otherwise, return just a single value.

    Returns
    -------
    cc : float, or tuple
       The value(s) of the clustering coefficient.
    
    References
    ----------
    "Clustering Coefficients in Multiplex Networks", E. Cozzo et al. , arXiv:1307.6780 [physics.soc-ph]

    See also
    --------
    avg_lcc_aw : The local alternating walks clustering coefficient averaged over all node-layer pairs.
    sncc_aw : The super-node version of the alternating walks clustering coefficient.
    gcc_aw : The global version of the alternating walks clustering coeffient.
    """
    aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=elementary_cycles(net,node,layer,anet=anet)
    t1=aaa
    d1=afa
    t2=aacac+acaac+acaca
    d2=afcac+acfac+acfca
    t3=acacac
    d3=acfcac

    if d3!=0:
        c3=t3/float(d3)
    else:
        c3=0
    if d2!=0:
        c2=t2/float(d2)
    else:
        c2=0
    if d1!=0:
        c1=t1/float(d1)
    else:
        c1=0

    if returnCVector:
        return c1,c2,c3

    if w3!=None:
        return w1*c1+w2*c2+w3*c3
    else:
        a,b=w1,w2
        t=t1*a**3 + t2*a*b*b + t3*b**3
        d=d1*a**3 + d2*a*b*b + d3*b**3        
        if d!=0:
            return t/float(d)
        else:
            return 0

def avg_lcc_aw(net,w1=1./2.,w2=1./2.,w3=None,returnCVector=False,anet=None):
    r"""Average value of the local version of the alternating walker clustering coefficient for multiplex networks.

    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    w1,w2,w3 : weights of the contributions of different layers.
       If w3 is set to None then w1 and w2 correspond to the "costs" of staying at a layer and
       changing the layer, i.e. w1 = :math:`\beta` and w2 = :math:`\gamma`
    returnCVector : bool
       If True, returns a vector containing the three different local clustering coefficients
       :math:`c_1,c_2,c_3`. Otherwise, return just a single value.

    Returns
    -------
    cc : float, or tuple
       The value(s) of the clustering coefficient.
    
    References
    ----------
    "Clustering Coefficients in Multiplex Networks", E. Cozzo et al. , arXiv:1307.6780 [physics.soc-ph]

    See also
    --------
    lcc_aw : The alternating walks clustering coefficient of a single node-layer pair.
    sncc_aw : The super-node version of the alternating walks clustering coefficient.
    gcc_aw : The global version of the alternating walks clustering coeffient.
    """
    c,c1,c2,c3=0,0,0,0
    n=0.
    for layer in net.slices[1]:
        for node in net.A[layer]:
            n+=1.
            if returnCVector:
                tc1,tc2,tc3=lcc_aw(net,node,layer,returnCVector=True,anet=anet)
                c1,c2,c3=c1+tc1,c2+tc2,c3+tc3
            else:
                c+=lcc_aw(net,node,layer,w1=w1,w2=w2,w3=w3)
                
    if returnCVector:
        return c1/n,c2/n,c3/n
    else:
        return c/n


def sncc_aw(net,node,w1=1./2.,w2=1./2.,w3=None,returnCVector=False,anet=None):
    r"""The super-node version of the alternating walker clustering coefficient for multiplex networks.

    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    node : any object
       The focal node. Given as node index in the network.
    w1,w2,w3 : weights of the contributions of different layers.
       If w3 is set to None then w1 and w2 correspond to the "costs" of staying at a layer and
       changing the layer, i.e. w1 = :math:`\beta` and w2 = :math:`\gamma`
    returnCVector : bool
       If True, returns a vector containing the three different local clustering coefficients
       :math:`c_1,c_2,c_3`. Otherwise, return just a single value.

    Returns
    -------
    cc : float, or tuple
       The value(s) of the clustering coefficient.
    
    References
    ----------
    "Clustering Coefficients in Multiplex Networks", E. Cozzo et al. , arXiv:1307.6780 [physics.soc-ph]

    See also
    --------
    lcc_aw : The alternating walks clustering coefficient of a single node-layer pair.
    avg_lcc_aw : The local alternating walks clustering coefficient averaged over all node-layer pairs.
    gcc_aw : The global version of the alternating walks clustering coeffient.
    """
    #t1,t2,t3,d1,d2,d3=0,0,0,0,0,0
    #for layer in net.slices[1]:
    #    aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=elementary_cycles(net,node,layer,anet=anet)
    #    t1+=aaa
    #    d1+=afa
    #    t2+=aacac+acaac+acaca
    #    d2+=afcac+acfac+acfca
    #    t3+=acacac
    #    d3+=acfcac

    aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=elementary_cycles(net,node,None,anet=anet)
    t1=aaa
    d1=afa
    t2=aacac+acaac+acaca
    d2=afcac+acfac+acfca
    t3=acacac
    d3=acfcac

    if d3!=0:
        c3=t3/float(d3)
    else:
        c3=0
    if d2!=0:
        c2=t2/float(d2)
    else:
        c2=0
    if d1!=0:
        c1=t1/float(d1)
    else:
        c1=0

    if returnCVector:
        return c1,c2,c3

    if w3!=None:
        return w1*c1+w2*c2+w3*c3
    else:
        a,b=w1,w2
        t=t1*a**3 + t2*a*b*b + t3*b**3
        d=d1*a**3 + d2*a*b*b + d3*b**3        
        if d!=0:
            return t/float(d)
        else:
            return 0

def sncc_aw_layercost(net,supernode,a=0.5,b=0.5):
    t1,t2,t3,d1,d2,d3=0,0,0,0,0,0
    for layer in net.slices[1]:
        aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc_cycle_vector_bf(net,supernode,layer,undefReturn=0.0)
        t1+=aaa
        d1+=afa
        t2+=aacac+acaac+acaca
        d2+=afcac+acfac+acfca
        t3+=acacac
        d3+=acfcac

    if float(a**3*d1+a*b**2*d2+b**3*d3)!=0:        
        return (a**3*t1+a*b**2*t2+b**3*t3)/float(a**3*d1+a*b**2*d2+b**3*d3)
    else:
        return 0



def gcc_aw(net,w1=1./2.,w2=1./2.,w3=None,returnCVector=False):
    r"""The global version of the alternating walker clustering coefficient for multiplex networks.

    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    w1,w2,w3 : weights of the contributions of different layers.
       If w3 is set to None then w1 and w2 correspond to the "costs" of staying at a layer and
       changing the layer, i.e. w1 = :math:`\beta` and w2 = :math:`\gamma`
    returnCVector : bool
       If True, returns a vector containing the three different global clustering coefficients
       :math:`c_1,c_2,c_3`. Otherwise, return just a single value.

    Returns
    -------
    cc : float, or tuple
       The value(s) of the clustering coefficient.
    
    References
    ----------
    "Clustering Coefficients in Multiplex Networks", E. Cozzo et al. , arXiv:1307.6780 [physics.soc-ph]

    See also
    --------
    lcc_aw : The alternating walks clustering coefficient of a single node-layer pair.
    avg_lcc_aw : The local alternating walks clustering coefficient averaged over all node-layer pairs.
    sncc_aw : The super-node version of the alternating walks clustering coefficient.
    """
    t1,t2,t3,d1,d2,d3=0,0,0,0,0,0
    #for layer in net.slices[1]:
    #    for node in net.A[layer]:#net.slices[0]:
    #        aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc_cycle_vector_bf(net,node,layer,undefReturn=0.0)
    #        t1+=aaa
    #        d1+=afa
    #        t2+=aacac+acaac+acaca
    #        d2+=afcac+acfac+acfca
    #        t3+=acacac
    #        d3+=acfcac
    #        #print node,layer,aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac

    aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=elementary_cycles(net)
    t1=aaa
    d1=afa
    t2=aacac+acaac+acaca
    d2=afcac+acfac+acfca
    t3=acacac
    d3=acfcac

    if d3!=0:
        c3=t3/float(d3)
    else:
        c3=0
    if d2!=0:
        c2=t2/float(d2)
    else:
        c2=0
    if d1!=0:
        c1=t1/float(d1)
    else:
        c1=0

    if returnCVector:
        return c1,c2,c3

    if w3!=None:
        return w1*c1+w2*c2+w3*c3
    else:
        a,b=w1,w2
        t=t1*a**3 + t2*a*b*b + t3*b**3
        d=d1*a**3 + d2*a*b*b + d3*b**3        
        if d!=0:
            return t/float(d)
        else:
            return 0


def gcc_moreno2_seplayers(net,w1=1./3.,w2=1./3.,w3=1./3.):
    """ If w3==None: w1 = \alpha and w2 =\beta
    """
    t1,t2,t3,d1,d2,d3=0,0,0,0,0,0
    for layer in net.slices[1]:
        for node in net.A[layer]:#net.slices[0]:
            aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc_cycle_vector_bf(net,node,layer,undefReturn=0.0)
            t1+=aaa
            d1+=afa
            t2+=2*aacac+2*acaac+acaca
            d2+=2*afcac+2*acfac+acfca
            t3+=2*acacac
            d3+=2*acfcac
            #print node,layer,aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac

    if w3!=None: 
        if d3!=0:
            c3=t3/float(d3)
        else:
            c3=0
        if d2!=0:
            c2=t2/float(d2)
        else:
            c2=0
        if d1!=0:
            c1=t1/float(d1)
        else:
            c1=0

        return w1*c1+w2*c2+w3*c3
    else:
        a,b=w1,w2
        t=t1*a**3 + t2*a*b*b + t3*b**3
        d=d1*a**3 + d2*a*b*b + d3*b**3        
        if d!=0:
            return t/float(d)
        else:
            return 0



def sncc_aw_seplayers(net,supernode,w1=1./3.,w2=1./3.,w3=1./3.,undefined=None):
    t1,t2,t3,d1,d2,d3=0,0,0,0,0,0
    for layer in net.slices[1]:
        aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc_cycle_vector_bf(net,supernode,layer,undefReturn=0.0)
        t1+=aaa
        d1+=afa
        t2+=aacac+acaac+acaca
        d2+=afcac+acfac+acfca
        t3+=acacac
        d3+=acfcac

    if d1==0:
        if w1>0:
            return undefined
        else:
            c1=0
    else:
        c1=t1/float(d1)
    if d2==0:
        if w2>0:
            return undefined
        else:
            c2=0
    else:
        c2=t2/float(d2)
    if d3==0:
        if w3>0:
            return undefined
        else:
            c3=0
    else:
        c3=t3/float(d3)
    return w1*c1+w2*c2+w3*c3


def gcc_from_lcc(net,lcc):
    lcc_vector=map(lambda node:lcc(net,node,undefReturn=None),net)
    lcc_fvector=filter(lambda x:x!=None,lcc_vector)
    if len(lcc_fvector)>0:
        return sum(lcc_fvector)/len(lcc_fvector)
    else:
        return None


def gcc_vector_moreno(net):
    def get_nom_den(p,ph):
        nom=0.0
        for i in range(len(p)):
            nom+=p[i,i]

        den=0.0
        for i in range(len(p)):
            for j in range(len(p)):
                if i!=j:
                    den+=ph[i,j]
        return nom,den

    import numpy
    adj,nodes1=net.get_supra_adjacency_matrix()    
    a,nodes2=net.get_supra_adjacency_matrix(includeCouplings=False)
    c=adj-a

    aaa=a*a*a
    aa=a*a
    c1_nom,c1_den=get_nom_den(aaa,aa)

    p21=a*a*c*a*c + c*a*c*a*a + a*c*a*a*c + c*a*a*c*a + a*c*a*c*a
    ph21=a*a*c + c*a*c*a + a*c*a + c*a*a*c + a*c*a*c
    c2_nom,c2_den=get_nom_den(p21,ph21)
    
    p111=a*c*a*c*a*c + c*a*c*a*c*a #????
    ph111=a*c*a*c + c*a*c*a*c #????
    c3_nom,c3_den=get_nom_den(p111,ph111)

    return c1_nom/float(c1_den),c2_nom/float(c2_den),c3_nom/float(c3_den)

def gcc_moreno(net,w1=1./3.,w2=1./3.,w3=1./3.):
    c1,c2,c3=gcc_vector_moreno(net)
    return w1*c1+w2*c2+w3*c3

def get_full_multiplex_network(nodes,layers):
    n=MultiplexNetwork(couplings=[('categorical',1.0)])
    for layer in layers:
        for node1 in nodes:
            for node2 in nodes:
                if node1!=node2:
                    n[node1,node2,layer,layer]=1
    return n

def gcc_vector_moreno2(net):
    def get_nom_den(p,ph):
        nom=0.0
        for i in range(len(p)):
            nom+=p[i,i]

        den=0.0
        for i in range(len(p)):
            den+=ph[i,i]
        return nom,den

    import numpy
    adj,nodes1=net.get_supra_adjacency_matrix()    
    a,nodes2=net.get_supra_adjacency_matrix(includeCouplings=False)
    c=adj-a

    fn=get_full_multiplex_network(net.slices[0],net.slices[1])
    f,node3=fn.get_supra_adjacency_matrix(includeCouplings=False)

    aaa=a*a*a
    afa=a*f*a
    c1_nom,c1_den=get_nom_den(aaa,afa)

    p21=a*a*c*a*c + c*a*c*a*a + a*c*a*a*c + c*a*a*c*a + a*c*a*c*a
    ph21=a*f*c*a*c + c*a*c*f*a + a*c*f*a*c + c*a*f*c*a + a*c*f*c*a
    c2_nom,c2_den=get_nom_den(p21,ph21)
    
    p111=a*c*a*c*a*c + c*a*c*a*c*a #????
    ph111=a*c*f*c*a*c + c*a*c*f*c*a #????
    c3_nom,c3_den=get_nom_den(p111,ph111)

    if c3_den!=0:
        return c1_nom/float(c1_den),c2_nom/float(c2_den),c3_nom/float(c3_den)
    else:
        return c1_nom/float(c1_den),c2_nom/float(c2_den),0.0

def gcc_moreno2(net,w1=1./3.,w2=1./3.,w3=1./3.):
    c1,c2,c3=gcc_vector_moreno2(net)
    if len(net.slices[1])==2:
        return w1*c1+w2*c2
    return w1*c1+w2*c2+w3*c3

def gcc_contraction_m(net):
    num=0
    nodes=net.slices[0]
    layers=net.slices[1]
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            num+=net[a,b,g,d]*net[b,e,d,n]*net[e,a,n,g]
    den=0
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            den+=net[a,b,g,d]*net[b,e,d,n]*1

    for a in nodes:
        for b in nodes:
            for g in layers:
                for d in layers:
                    den+= -net[a,b,g,d]*net[b,a,d,g]

    if den!=0:
        return num/float(den)
    else:
        return None

def gcc_contraction_m_ct(net):
    num=0
    nodes=net.slices[0]
    layers=net.slices[1]
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            num+=net[a,b,g,d]*net[b,e,d,n]*net[e,a,n,g]
    den=0
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            den+=net[a,b,g,d]*net[b,e,d,n]*1
                            if e==a and n==g:
                                den+= net[a,b,g,d]*net[b,e,d,n]*(-1)

    if den!=0:
        return num/float(den)
    else:
        return None


def gcc_contraction_m_full(net):
    num=0
    nodes=net.slices[0]
    layers=net.slices[1]
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            num+=net[a,b,g,d]*net[b,e,d,n]*net[e,a,n,g]

    den=0
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            if b!=e or d!=n:
                                den+=net[a,b,g,d]*1*net[e,a,n,g]

    if den!=0:
        return num/float(den)
    else:
        return None



def gcc_contraction_o(net):
    num=0
    nodes=net.slices[0]
    layers=net.slices[1]
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            num+=net[a,b,g,g]*net[b,e,d,d]*net[e,a,n,n]
    den=0
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            den+=net[a,b,g,g]*net[b,e,d,d]*1
                            #if net[a,b,g,g]*net[b,e,d,d]*1>0:
                            #    print a,b,e,g,d,n

    for a in nodes:
        for b in nodes:
            for g in layers:
                for d in layers:
                    den+= -net[a,b,g,g]*net[b,a,d,d]
   # print num,den
    if den!=0:
        return num/float(den)
    else:
        return None


def gcc_contraction_o_full(net):
    num=0
    nodes=net.slices[0]
    layers=net.slices[1]
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            num+=net[a,b,g,g]*net[b,e,d,d]*net[e,a,n,n]
    den=0
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            if b!=e:
                                den+=net[a,b,g,g]*1*net[e,a,n,n]

    if den!=0:
        return num/float(den)
    else:
        return None



def gcc_contraction_o2(net):
    num=0
    nodes=net.slices[0]
    layers=net.slices[1]
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            num+=net[a,b,g,g]*net[b,e,d,d]*net[e,a,n,n]
    den=0
    for a in nodes:
        for b in nodes:
            for e in nodes:
                for g in layers:
                    for d in layers:
                        for n in layers:
                            den+=net[a,b,g,g]*net[b,e,d,d]*1
                            if e==a:
                                den+= net[a,b,g,g]*net[b,e,d,d]*(-1)
                            #if net[a,b,g,g]*net[b,e,d,d]*1>0:
                            #    print a,b,e,g,d,n

    #for a in nodes:
    #    for b in nodes:
    #        for g in layers:
    #            for d in layers:
    #                den+= -net[a,b,g,g]*net[b,a,d,d]*len(layers)
   # print num,den
    if den!=0:
        return num/float(den)
    else:
        return None


def lcc_brodka(net,node,anet=None,threshold=1,undefReturn=0.0):
    r"""The "cross-layer clustering coefficient" defined by Brodka et al. 

    The clustering coefficient for node :math:`u` is given by the formula (see Ref. [2]):
    
    .. math:: c_{Br,u,t} = \frac{\sum_{\alpha \in L} \sum_{v \in N(u,t)} \sum_{h \in N(u,t)}( \mathcal{W}_{hv\alpha} + \mathcal{W}_{vh\alpha})}{2 |N(u,t)| |L|},

    where :math:`N(u,t) = \{ v : | \{\alpha : \mathcal{A}_{uv\alpha}=1 \wedge \mathcal{A}_{vu\alpha}=1 \}| \leq t \} `,  
    :math:`L` is the set of layers,  :math:`\mathcal{W}` is the rank-3 weighted adjacency tensor of the multiplex network, 
    and :math:`\mathcal{A}` is the rank-3 unweighted adjacency tensor of the multiplex network.
       
    One can get the "multi-layered clustering coefficient in extendend neighborhood" by setting the threshold to one :math:`t=1`, and 
    the "multi-layered clustering coefficient in reduced neighborhood" by setting the threshold to the total number of layers 
    :math:`t=|L|`.

    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    node : any object
       The focal node. Given as the node index in the network.
    anet : MultilayerNetwork with aspects=0
       The aggregated network. If given, it is used to speed up the calculation. NOTE: for undirected networks the
       "normal" aggregation strategy (produced for example by the aggregate function in this library) is suitable,
       but for directed networks the network needs to be aggregated such that thresholding it will produce the 
       neighborhood sets :math:`N(u,t)`.
    threshold : int, string
       Threshold for number of layers, see Ref. [2]. If 'all', then the threshold is the total number of layers.

    Returns
    -------
    float or object
       The clustering coefficient value.

    References
    ----------
    [1] "A Method for Group Extraction in Complex Social Networks", Piotr Brodka, Katarzyna Musial, Przemyslaw Kazienko,In
    M. D. Lytras, P. Ordonez De Pablos, A. Ziderman, A. Roulstone, H. Maurer, and J. B. Imber, editors,
    Knowledge Management, Information Systems, E-Learning, and Sustainability Research, volume 111
    of Communications in Computer and Information Science, pages 238-247. Springer Berlin Heidelberg, 2010.

    [2] P. Brodka, P. Kazienko, K. Musial, and K. Skibicki. Analysis of Neighbourhoods in Multi-layered
    Dynamic Social Networks. International Journal of Computational Intelligence Systems, 5(3):582-596,
    2012.

    Notes
    -----
    This clustering coefficient doesn't return to the typical unweighted clustering coefficient when the edge weights
    are binary and there is only a single layer. Further, it is not normalized in a way that it's values would be 
    between 0 an 1. For example, consider a full multiplex network with n nodes and arbitrary number of layers. 
    In this case this clustering cofficient will take value n-2 for all the nodes.

    Multiplying all the weights by a constant c will cause the clustering coefficient values to be multiplied by c.

    See also
    --------
    lcc_aw : Local multiplex clustering coefficient defined by Cozzo et al.
    cc_barrett : Local multiplex clustering coefficient defined by Barrett et al.
    """
    assert net.aspects==1

    if threshold=='all':
        threshold=len(net.get_layers())

    thneighborhood=[]
    if anet==None or net.directed:
        neighborcount={}
        for layer in net.get_layers():
            for neigh in net.A[layer][node].iter_total():
                neighborcount[neigh]=neighborcount.get(neigh,0)+1            
                thneighborhood=[]
        #for neighbor,count in neighborcount.iteritems():            
        for neighbor in neighborcount:
            count=neighborcount[neighbor]
            if count >= threshold:
                thneighborhood.append(neighbor)
    else:
        for neighbor in anet[node]:
            if anet[node,neighbor]>=threshold:
                thneighborhood.append(neighbor)

    if len(thneighborhood)==0:
        return 0.0

    s=0
    if anet==None:
        for layer in net.get_layers():
            for v in thneighborhood:
                for h in thneighborhood:
                    s+=net[h,v,layer]+net[v,h,layer]
    else:
        for v in thneighborhood:
            for h in thneighborhood:
                s+=anet[h,v]+anet[v,h]

    if len(thneighborhood)*len(net.get_layers())==0:
        return undefReturn
    else:
        return s/float(2*len(thneighborhood)*len(net.get_layers()))



def lcc_battiston1(net,node,undefReturn=0.0):
    r"""The first local clustering coefficient defined by Battiston et al.

    The clustering coefficient for node :math:`u` is given by the formula (see Ref. [1]):
    
    .. math:: c_{Bat1,u} = \frac{\sum_{\alpha \in L} \sum_{\beta \in L,\beta \neq \alpha } \sum_{v,h \in V, v \neq u, h \neq u} \mathcal{A}_{uv\alpha} \mathcal{A}_{vh\beta} \mathcal{A}_{hu\alpha}}{\sum_{\alpha \in L}\sum_{v,h \in V, v \neq u, h \neq u} \mathcal{A}_{uv\alpha} \mathcal{A}_{hu\alpha}},

    where :math:`V` is the set of nodes, :math:`L` is the set of layers and :math:`\mathcal{A}` is the rank-3 unweighted adjacency tensor of the multiplex network.

    lcc_battiston1 is only defined for single-aspect node-aligned multiplex networks with 2 or more layers.
       
    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    node : any object
       The focal node. Given as the node index in the network.

    Returns
    -------
    float or object
       The clustering coefficient value, or the undefReturn value if the clustering
       coefficient is not defined for the node.

    References
    ----------
    [1] "Metrics for the analysis of multiplex networks", Federico Battiston, Vincenzo Nicosia, Vito Latora,
    arXiv:1308.3182v2 (2013)

    Notes
    -----
    lcc_battiston1 is not normalized such that it would take values between 0 and 1. For example, for full multiplex
    networks with n nodes and b layers it takes values (n-1)/(n-2).

    See also
    --------
    lcc_aw : Local multiplex clustering coefficient defined by Cozzo et al.
    cc_barrett : Local multiplex clustering coefficient defined by Barrett et al.
    """

    assert net.aspects==1
    assert len(net.get_layers())>=2

    d=0
    for alpha in net.get_layers():
        for v in net:
            if v!=node:
                for h in net:
                    if h!=node:
                        if net[node,v,alpha] != net.noEdge and net[h,node,alpha] != net.noEdge:
                            d+=1
    if d==0:
        return undefReturn

    s=0

    for alpha in net.get_layers():
        for beta in net.get_layers():
            if beta!=alpha:
                for v in net:
                    if v!=node:
                        for h in net:
                            if h!=node:
                                if net[node,v,alpha] != net.noEdge and net[v,h,beta] != net.noEdge and net[h,node,alpha] != net.noEdge:
                                    s+=1
    b=len(net.get_layers())
    return s/float(d)/float(b-1)




def lcc_battiston2(net,node,undefReturn=0.0):
    r"""The second local clustering coefficient defined by Battiston et al.

    The clustering coefficient for node :math:`u` is given by the formula (see Ref. [1]):
    
    .. math:: c_{Bat2,u} = \frac{\sum_{\alpha \in L} \sum_{\beta \in L,\beta \neq \alpha } \sum_{\gamma \in L,\gamma \neq \alpha, \beta } \sum_{v,h \in V, v \neq u, h \neq u} \mathcal{A}_{uv\alpha} \mathcal{A}_{vh\gamma} \mathcal{A}_{hu\beta}}{\sum_{\alpha \in L} \sum_{\beta \in L,\beta \neq \alpha }\sum_{v,h \in V, v \neq u, h \neq u} \mathcal{A}_{uv\alpha} \mathcal{A}_{hu\beta}},

    where :math:`V` is the set of nodes, :math:`L` is the set of layers and :math:`\mathcal{A}` is the rank-3 unweighted adjacency tensor of the multiplex network.

    lcc_battiston2 is only defined for single-aspect node-aligned multiplex networks with 3 or more layers.
       
    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    node : any object
       The focal node. Given as the node index in the network.

    Returns
    -------
    float or object
       The clustering coefficient value, or the undefReturn value if the clustering
       coefficient is not defined for the node.

    References
    ----------
    [1] "Metrics for the analysis of multiplex networks", Federico Battiston, Vincenzo Nicosia, Vito Latora,
    arXiv:1308.3182v2 (2013)

    Notes
    -----
    lcc_battiston2 is not normalized such that it would take values between 0 and 1. For example, for full multiplex
    networks with n nodes and b layers it takes values (n-1)/(n-2).

    See also
    --------
    lcc_aw : Local multiplex clustering coefficient defined by Cozzo et al.
    cc_barrett : Local multiplex clustering coefficient defined by Barrett et al.
    """

    assert net.aspects==1

    if len(net.get_layers())<3:
        return undefReturn

    d=0
    for alpha in net.get_layers():
        for beta in net.get_layers():
            if beta!=alpha:
                for v in net:
                    if v!=node:
                        for h in net:
                            if h!=node:
                                if net[node,v,alpha] != net.noEdge and net[h,node,beta] != net.noEdge:
                                    d+=1
    if d==0:
        return undefReturn

    s=0

    for alpha in net.get_layers():
        for beta in net.get_layers():
            if beta!=alpha:
                for gamma in net.get_layers():
                    if gamma != alpha and gamma != beta:
                        for v in net:
                            if v!=node:
                                for h in net:
                                    if h!=node:
                                        if net[node,v,alpha] != net.noEdge and net[v,h,gamma] != net.noEdge and net[h,node,beta] != net.noEdge:
                                            s+=1
    b=len(net.get_layers())                                       
    return s/float(d)/float(b-2)



def lcc_criado(net,node,undefReturn=0.0,anet=None):
    r"""The local clustering coefficient defined by Criado et al.

    The clustering coefficient for node :math:`u` is given by the formula (see Ref. [1]):
    
    .. math:: c_{Cr,u} = \frac{2 \sum_{\alpha \in L} | \bar{E_\alpha}(u) | }{\sum_{\alpha \in L} |\Gamma_\alpha (u)| (|\Gamma_\alpha (u) -1|)}

    where :math:`L` is the set of layers, :math:`\Gamma_\alpha (u)=\Gamma (u) \cap V_\alpha`, where :math:`\Gamma (u)` is the set of neighbors
    of node :math:`u` in the aggregated network and :math:`V_\alpha` is the set of nodes in layer :math:`\alpha`, and \bar{E_\alpha}(u) is the
    set of edges in the subgraph of the aggregated network spanned by :math:`\Gamma_\alpha (u)`.

    lcc_criado is only defined for a single-aspect multiplex network. The network doesn't need to be node-aligned.
       
    Parameters
    ----------
    net : MultiplexNetwork with aspects=1
       The input network.
    node : any object
       The focal node. Given as the node index in the network.

    Returns
    -------
    float or object
       The clustering coefficient value, or the undefReturn value if the clustering
       coefficient is not defined for the node.

    References
    ----------
    [1] "A mathematical model for networks with structures in the mesoscale", R. Criado, J. Flores, A. Garcia del Amo,
    J. Gomez-Gardenes, and M. Romance, Int. J. Comp. Math., 89(3):291-309 (2011)

    See also
    --------
    lcc_aw : Local multiplex clustering coefficient defined by Cozzo et al.
    cc_barrett : Local multiplex clustering coefficient defined by Barrett et al.
    """
    s,d=0,0
    
    if anet==None:
        nu=set()
        for alpha in net.get_layers():
            for neigh in net.A[alpha][node]:
                nu.add(neigh)
    else:
        nu=set(anet[node])

    for alpha in net.get_layers():
        nalphau=nu.intersection(set(net.A[alpha]))
        for neighbor1 in nalphau:
            for neighbor2 in net.A[alpha][neighbor1]:
                if neighbor2 in nalphau:
                    s+=1
        d+=len(nalphau)*(len(nalphau)-1)
    
    if d==0:
        return undefReturn
    else:
        return s/float(d)
        

