"""Clustering coefficients in multiplex networks.
"""

import itertools
from net import MultiplexNetwork

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
                #for layer in net.slices[1]:
                for layer in net._nodeToLayers[h]:
                    layer=layer[0]
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

def gcc_alternating_walks_vector_adj(net):
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




def gcc_alternating_walks_seplayers_adj(net,w1=1./3.,w2=1./3.,w3=1./3.,returnCVector=False):
    c1_nom,c1_den,c2_nom,c2_den,c3_nom,c3_den=gcc_alternating_walks_vector_adj(net)
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



def lcc_alternating_walks(net,node,layer,w1=1./3.,w2=1./3.,w3=1./3.,returnCVector=False):
    """ If w3==None: w1 = \alpha and w2 =\beta
    """
    aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc_cycle_vector_bf(net,node,layer,undefReturn=0.0)
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

def avg_lcc_alternating_walks(net,w1=1./3.,w2=1./3.,w3=1./3.,returnCVector=False):
    c,c1,c2,c3=0,0,0,0
    n=0.
    for layer in net.slices[1]:
        for node in net.A[layer]:
            n+=1.
            if returnCVector:
                tc1,tc2,tc3=lcc_alternating_walks(net,node,layer,returnCVector=True)
                c1,c2,c3=c1+tc1,c2+tc2,c3+tc3
            else:
                c+=lcc_alternating_walks_seplayers(net,node,layer,w1=w1,w2=w2,w3=w3)
                
    if returnCVector:
        return c1/n,c2/n,c3/n
    else:
        return c/n


def gcc_alternating_walks_seplayers(net,w1=1./3.,w2=1./3.,w3=1./3.,returnCVector=False):
    """ If w3==None: w1 = \alpha and w2 =\beta
    """
    t1,t2,t3,d1,d2,d3=0,0,0,0,0,0
    for layer in net.slices[1]:
        for node in net.A[layer]:#net.slices[0]:
            aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc_cycle_vector_bf(net,node,layer,undefReturn=0.0)
            t1+=aaa
            d1+=afa
            t2+=aacac+acaac+acaca
            d2+=afcac+acfac+acfca
            t3+=acacac
            d3+=acfcac
            #print node,layer,aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac


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


def sncc_alternating_walks(net,supernode,a=0.5,b=0.5):
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

def sncc_alternating_walks_seplayers(net,supernode,w1=1./3.,w2=1./3.,w3=1./3.,undefined=None):
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
