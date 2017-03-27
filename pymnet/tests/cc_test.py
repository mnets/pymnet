import unittest
from operator import itemgetter
import sys

from pymnet import net,cc,models,transforms
import itertools
import random
import pymnet.net

class TestCC(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_unweighted_flat_triangle(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=1
        n[2,3]=1
        n[3,1]=1

        self.assertEqual(cc.lcc(n,1),1.0)
        self.assertEqual(cc.cc_zhang(n,1),1.0)
        self.assertEqual(cc.cc_onnela(n,1),1.0)
        self.assertEqual(cc.cc_barrat(n,1),1.0)


    def test_unweighted_flat_simple(self):
        n=net.MultilayerNetwork(aspects=0)
        n[1,2]=1
        n[2,3]=1
        n[3,1]=1
        n[1,4]=1

        self.assertEqual(cc.lcc(n,1),1./3.)
        self.assertEqual(cc.cc_zhang(n,1),1./3.)
        self.assertEqual(cc.cc_onnela(n,1),1./3.)
        self.assertEqual(cc.cc_barrat(n,1),1./3.)

    def test_weighted_flat_simple(self):
        pass #TODO

    def test_unweighted_mplex_clique(self):
        def clique_net(nodes,levels):
            n=net.MultiplexNetwork([('categorical',1.0)],directed=False)
            for level in range(levels):
                for i,j in itertools.combinations(range(nodes),2):
                    n[i,j,level]=1

            an=net.MultilayerNetwork(aspects=0,directed=False)
            for i,j in itertools.combinations(range(nodes),2):
                an[i,j]=levels

            return n,an
        
        n,an=clique_net(3,4) # 3 nodes, 4 layers

        #barrett
        self.assertEqual(cc.cc_barrett(n,1,an),128./96.)
        self.assertEqual(cc.cc_barrett(n,1,an),cc.cc_barrett_explicit(n,1))

        #cc seq
        self.assertEqual(cc.cc_sequence(n,1),([1,1,1,1],[1,1,1,1]))

        #Brodka et al.
        self.assertEqual(cc.lcc_brodka(n,1,threshold=1),1.0)
        self.assertEqual(cc.lcc_brodka(n,1,threshold=3),1.0)
        self.assertEqual(cc.lcc_brodka(n,1,threshold='all'),1.0)

        self.assertEqual(cc.lcc_brodka(n,1,threshold=1,anet=an),1.0)
        self.assertEqual(cc.lcc_brodka(n,1,threshold=3,anet=an),1.0)
        self.assertEqual(cc.lcc_brodka(n,1,threshold='all',anet=an),1.0)

        #Battiston et al.
        #self.assertEqual(cc.lcc_battiston1(n,1),3./2.) #(b-1)(n-1)/(n-2)
        #self.assertEqual(cc.lcc_battiston2(n,1),2./2.) #(b-2)(n-1)/(n-2)
        self.assertEqual(cc.lcc_battiston1(n,1),3./6.) #(n-1)/(n-2)
        self.assertEqual(cc.lcc_battiston2(n,1),2./4.) #(n-1)/(n-2)

        #Criado et al.
        self.assertEqual(cc.lcc_criado(n,1),1.)
        self.assertEqual(cc.lcc_criado(n,1,anet=an),1.)

        n,an=clique_net(7,4) # 7 nodes, 4 layers

        #Brodka et al.
        self.assertEqual(cc.lcc_brodka(n,1,threshold=1),5.0) #nodes - 2
        self.assertEqual(cc.lcc_brodka(n,1,threshold=3),5.0)
        self.assertEqual(cc.lcc_brodka(n,1,threshold='all'),5.0)

        self.assertEqual(cc.lcc_brodka(n,1,threshold=1,anet=an),5.0) 
        self.assertEqual(cc.lcc_brodka(n,1,threshold=3,anet=an),5.0)
        self.assertEqual(cc.lcc_brodka(n,1,threshold='all',anet=an),5.0)

        #Battiston et al.
        #self.assertEqual(cc.lcc_battiston1(n,1),3.*5./6.) #(b-1)(n-1)/(n-2)
        #self.assertEqual(cc.lcc_battiston2(n,1),2.*5./6.) #(b-2)(n-1)/(n-2)
        self.assertEqual(cc.lcc_battiston1(n,1),3.*5./18.) #(n-1)/(n-2)
        self.assertEqual(cc.lcc_battiston2(n,1),2.*5./12.) #(n-1)/(n-2)

        #Criado et al.
        self.assertEqual(cc.lcc_criado(n,1),1.)
        self.assertEqual(cc.lcc_criado(n,1,anet=an),1.)

    def test_unweighted_mplex_simple(self):
        n=net.MultiplexNetwork([('categorical',1.0)])

        n[1,2,1]=1
        n[1,3,1]=1
        n[2,3,1]=1

        n[1,2,2]=1
        n[1,3,2]=1
        n[1,4,2]=1
        n[3,4,2]=1

        n[1,2,3]=1
        n[1,3,3]=1
        n[1,4,3]=1
        n[2,4,3]=1

        an=net.MultilayerNetwork(aspects=0)
        an[1,2]=3
        an[1,3]=3
        an[1,4]=2
        an[2,3]=1
        an[3,4]=1
        an[2,4]=1

        for i in range(4):
            self.assertEqual(cc.cc_barrett(n,i,an),cc.cc_barrett_explicit(n,i))

        self.assertEqual(cc.lcc_brodka(n,1,anet=None,threshold=1),2./3.)
        self.assertEqual(cc.lcc_brodka(n,2,anet=None,threshold=1),4./3.)
        self.assertEqual(cc.lcc_brodka(n,3,anet=None,threshold=1),4./3.)
        self.assertEqual(cc.lcc_brodka(n,4,anet=None,threshold=1),14./9.)
        self.assertEqual(cc.lcc_brodka(n,1,anet=an,threshold=1),2./3.)
        self.assertEqual(cc.lcc_brodka(n,2,anet=an,threshold=1),4./3.)
        self.assertEqual(cc.lcc_brodka(n,3,anet=an,threshold=1),4./3.)
        self.assertEqual(cc.lcc_brodka(n,4,anet=an,threshold=1),14./9.)

        self.assertEqual(cc.lcc_brodka(n,1,anet=None,threshold=2),2./3.)
        self.assertEqual(cc.lcc_brodka(n,2,anet=None,threshold=2),0.)
        self.assertEqual(cc.lcc_brodka(n,3,anet=None,threshold=2),0.)
        self.assertEqual(cc.lcc_brodka(n,4,anet=None,threshold=2),0.)
        self.assertEqual(cc.lcc_brodka(n,1,anet=an,threshold=2),2./3.)
        self.assertEqual(cc.lcc_brodka(n,2,anet=an,threshold=2),0.)
        self.assertEqual(cc.lcc_brodka(n,3,anet=an,threshold=2),0.)
        self.assertEqual(cc.lcc_brodka(n,4,anet=an,threshold=2),0.)

        self.assertEqual(cc.lcc_brodka(n,1,anet=None,threshold=3),1./3.)
        self.assertEqual(cc.lcc_brodka(n,2,anet=None,threshold=3),0.)
        self.assertEqual(cc.lcc_brodka(n,3,anet=None,threshold=3),0.)
        self.assertEqual(cc.lcc_brodka(n,4,anet=None,threshold=3),0.)
        self.assertEqual(cc.lcc_brodka(n,1,anet=an,threshold=3),1./3.)
        self.assertEqual(cc.lcc_brodka(n,2,anet=an,threshold=3),0.)
        self.assertEqual(cc.lcc_brodka(n,3,anet=an,threshold=3),0.)
        self.assertEqual(cc.lcc_brodka(n,4,anet=an,threshold=3),0.)

    def test_directed_unweighted(self):
        """The 3-layer multiplex networks example from Brodka et al. 'Analysis of Neighborhoods of in Multi-layered
        Dynamic Social Networks', 2012"""
        n=net.MultiplexNetwork(['categorical'],directed=True)

        n['x','z',1]=1
        n['x','y',1]=1
        n['y','x',1]=1
        n['y','z',1]=1
        n['z','x',1]=1
        n['z','t',1]=1
        n['u','x',1]=1
        n['u','z',1]=1
        n['u','v',1]=1
        n['v','u',1]=1
        n['v','t',1]=1
        n['t','z',1]=1
        n['t','v',1]=1

        n['x','u',2]=1
        n['x','z',2]=1
        n['x','v',2]=1
        n['x','y',2]=1
        n['z','x',2]=1
        n['u','v',2]=1
        n['v','u',2]=1
        n['v','x',2]=1
        n['v','y',2]=1

        n['x','u',3]=1
        n['x','z',3]=1
        n['x','v',3]=1
        n['x','y',3]=1
        n['y','z',3]=1
        n['y','v',3]=1
        n['z','x',3]=1
        n['z','y',3]=1
        n['z','t',3]=1
        n['u','x',3]=1
        n['v','x',3]=1
        n['v','t',3]=1
        n['t','z',3]=1
        n['t','v',3]=1

        an=net.MultilayerNetwork(aspects=0,directed=True)

        an['x','z']=3
        an['x','u']=2
        an['x','v']=2
        an['x','y']=3
        an['y','x']=1
        an['y','z']=2
        an['y','v']=1
        an['z','x']=3
        an['z','y']=1
        an['z','t']=2
        an['u','x']=2
        an['u','z']=1
        an['u','v']=2
        an['v','x']=2
        an['v','y']=1
        an['v','u']=2
        an['v','t']=2
        an['t','z']=2
        an['t','v']=2

        self.assertEqual(cc.lcc_brodka(n,'t',threshold=1),0.0)
        self.assertEqual(cc.lcc_brodka(n,'t',threshold=2),0.0)
        self.assertEqual(cc.lcc_brodka(n,'t',threshold=3),0.0)
        self.assertEqual(cc.lcc_brodka(n,'z',threshold=1),2./3.)
        self.assertEqual(cc.lcc_brodka(n,'z',threshold=2),4./9.)
        self.assertEqual(cc.lcc_brodka(n,'z',threshold=3),0.0)

        self.assertEqual(cc.lcc_brodka(n,'t',anet=an,threshold=1),0.0)
        self.assertEqual(cc.lcc_brodka(n,'t',anet=an,threshold=2),0.0)
        self.assertEqual(cc.lcc_brodka(n,'t',anet=an,threshold=3),0.0)
        self.assertEqual(cc.lcc_brodka(n,'z',anet=an,threshold=1),2./3.)
        self.assertEqual(cc.lcc_brodka(n,'z',anet=an,threshold=2),4./9.)
        self.assertEqual(cc.lcc_brodka(n,'z',anet=an,threshold=3),0.0)

    def test_unweighted_consistency(self,net):
        anet=transforms.aggregate(net,1)
        onet=transforms.overlay_network(net)
        wmax=max(map(lambda x:x[2],anet.edges))
        owmax=max(map(lambda x:x[2],onet.edges))
        b=len(net.slices[1])

        self.assertEqual(cc.cc_cycle_vector_bf(net,1,1),cc.cc_cycle_vector_adj(net,1,1))

        #----
        t=0
        node=1
        for i,j in itertools.combinations(anet[node],2):
            t+=anet[node][i]*anet[node][j]*anet[i][j]
        d=0
        for i,j in itertools.combinations(anet[node],2):
            d+=anet[node][i]*anet[node][j]*len(net.slices[1])
        
        lt=0
        ld=0
        sums=[0 for i in range(10)]
        for l in net.slices[1]:
            aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc.cc_cycle_vector_bf(net,1,l)
            self.assertEqual((aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac),cc.cc_cycle_vector_anet(net,1,l,anet))            
            sums=map(lambda x,y:x+y,sums,[aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac])
            lt+= aaa+aacac+acaac+acaca+acacac
            ld+= afa+afcac+acfac+acfca+acfcac      
        self.assertEqual(tuple(sums), cc.cc_cycle_vector_anet(net,1,None,anet))
        self.assertEqual(2*t,lt)
        self.assertEqual(2*d,ld)

        cc.gcc_aw_vector_adj(net)

        self.assertAlmostEqual(cc.gcc_aw(net,w1=0.3,w2=0.3,w3=0.3),cc.gcc_aw_seplayers_adj(net,w1=0.3,w2=0.3,w3=0.3))

        for supernode in net.slices[0]:
            self.assertAlmostEqual(cc.sncc_aw(net,supernode,w1=0.5,w2=0.5,w3=None),wmax/float(b)*cc.cc_zhang(anet,supernode))

        #global cc
        tga=0
        tgaw=0
        tgmoreno=0
        for node in net:
            for i,j in itertools.combinations(anet[node],2):
                tga+=2*anet[node][i]*anet[node][j]*anet[i][j]
            for l in net.slices[1]:
                aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc.cc_cycle_vector_bf(net,node,l)
                tgaw+=aaa+aacac+acaac+acaca+acacac
                tgmoreno+=aaa+2*aacac+2*acaac+acaca+2*acacac
        """
        print "gcc",cc.gcc_contraction_m(net),cc.gcc_contraction_m_ct(net),cc.gcc_super_graph(net),cc.gcc_contraction_o2(net),owmax*cc.gcc_zhang(onet)/float(b),cc.gcc_contraction_o(net)
        """

    def test_symmetric_aw(self,net):
            import numpy
            adj,nodes1=net.get_supra_adjacency_matrix()    
            a,nodes2=net.get_supra_adjacency_matrix(includeCouplings=False)
            c=adj-a
            i=numpy.eye(len(a))
            ch=c+i

            b=len(net.slices[1])
            assert (c*c==(b-1)*i+(b-2)*c).all()
            
            #fn=cc.get_full_multiplex_network(net.slices[0],net.slices[1])
            #f,node3=fn.get_supra_adjacency_matrix(includeCouplings=False)

            #ca+ac version            
            t=(ch*a+a*ch)*(ch*a+a*ch)*(ch*a+a*ch)
            t_simple=4*(b+1)*a*a*a + 2*(b+2)*a*c*a*a*c + 4*a*a*c*a*c + 2*(b+1)*a*c*a*c*a + 2*a*c*a*c*a*c + 2*c*a*c*a*a*c + 2*c*a*a*a*c            
            for node in range(len(a)):
                assert t[node,node]==t_simple[node,node]

            #c'a+ac' version
            chd=c+0.5*i
            t=(chd*a+a*chd)*(chd*a+a*chd)*(chd*a+a*chd)
            t_simple=(2*b-1)*a**3 + 2*a**2*c*a*c+ 2*b*a*c*a**2*c+ (2*b-1)* a*c*a*c*a + 2*a*c*a*c*a*c + c*a**3*c+ 2*c*a**2*c*a*c
            for node in range(len(a)):
                assert t[node,node]==t_simple[node,node]

            #c'a+ac' version with random alpha and beta
            alpha,beta=random.random(),random.random()
            chd=beta*c+0.5*alpha*i
            t=(chd*a+a*chd)*(chd*a+a*chd)*(chd*a+a*chd)
            t_simple=alpha**3*a**3 - 2*alpha*beta**2*a**3 + 2*alpha*b*beta**2*a**3 + alpha*beta**2*c*a**3*c - 4*beta**3*a*c*a**2*c - 4*beta**3*a*c*a*c*a + 2*alpha*beta**2*a**2*c*a*c + 2*b*beta**3*a*c*a**2*c + 2*beta**3*c*a**2*c*a*c + 4*alpha*beta**2*a*c*a**2*c + 2*b*beta**3*a*c*a*c*a + 2*beta**3*a*c*a*c*a*c + 3*alpha*beta**2*a*c*a*c*a
            for node in range(len(a)):
                self.assertAlmostEqual(t[node,node],t_simple[node,node])

            #cac version with random alpha and beta
            alpha,beta=random.random(),random.random()
            ch=beta*c+alpha*i
            t=(ch*a*ch)*(ch*a*ch)*(ch*a*ch)
            t_simple=alpha**6*a**3 + alpha**2*beta**4*a**3 - 2*alpha**4*beta**2*a**3 + alpha**2*beta**4*b**2*a**3 + beta**6*c*a**3*c - 2*b*alpha**2*beta**4*a**3 + 2*b*alpha**4*beta**2*a**3 + alpha**4*beta**2*c*a**3*c + beta**6*b**2*c*a**3*c - 2*b*beta**6*c*a**3*c - 2*alpha**2*beta**4*c*a**3*c - 4*alpha**2*beta**4*a*c*a**2*c - 4*alpha**2*beta**4*a**2*c*a*c - 4*alpha**3*beta**3*a*c*a**2*c - 4*alpha**3*beta**3*a**2*c*a*c + 2*b*alpha**2*beta**4*c*a**3*c + 4*alpha*beta**5*a*c*a**2*c + 4*alpha*beta**5*a**2*c*a*c + 4*alpha**4*beta**2*a*c*a**2*c + 4*alpha**4*beta**2*a**2*c*a*c + 4*beta**6*c*a**2*c*a*c - 8*alpha**3*beta**3*a*c*a*c*a - 6*alpha*b*beta**5*a*c*a**2*c - 6*alpha*b*beta**5*a**2*c*a*c - 6*b*beta**6*c*a**2*c*a*c - 4*alpha*beta**5*c*a**2*c*a*c - 4*alpha**2*beta**4*c*a**2*c*a*c + 2*alpha*beta**5*b**2*a*c*a**2*c + 2*alpha*beta**5*b**2*a**2*c*a*c + 2*b*alpha**3*beta**3*a*c*a**2*c + 2*b*alpha**3*beta**3*a**2*c*a*c + 2*beta**6*b**2*c*a**2*c*a*c + 4*b*alpha**2*beta**4*a*c*a**2*c + 4*b*alpha**2*beta**4*a**2*c*a*c + 4*alpha**2*beta**4*a*c*a*c*a + 4*alpha**3*beta**3*c*a**2*c*a*c + 4*alpha**4*beta**2*a*c*a*c*a + alpha**2*beta**4*b**2*a*c*a*c*a - 16*alpha**2*beta**4*a*c*a*c*a*c - 4*b*alpha**2*beta**4*a*c*a*c*a + 2*b*alpha**2*beta**4*c*a**2*c*a*c + 4*alpha*b*beta**5*c*a**2*c*a*c + 4*b*alpha**3*beta**3*a*c*a*c*a + 4*beta**6*c*a*c*a*c*a*c + 8*alpha*beta**5*a*c*a*c*a*c + 8*alpha**3*beta**3*a*c*a*c*a*c + beta**6*b**2*c*a*c*a*c*a*c - 8*alpha*b*beta**5*a*c*a*c*a*c - 8*alpha*beta**5*c*a*c*a*c*a*c - 4*b*beta**6*c*a*c*a*c*a*c + 2*alpha*beta**5*b**2*a*c*a*c*a*c + 4*alpha**2*beta**4*c*a*c*a*c*a*c + 8*b*alpha**2*beta**4*a*c*a*c*a*c + 4*alpha*b*beta**5*c*a*c*a*c*a*c
            for node in range(len(a)):
                self.assertAlmostEqual(t[node,node],t_simple[node,node])

            #cac version
            ch=c+i
            t=(ch*a*ch)*(ch*a*ch)*(ch*a*ch)
            t_simple=b**2*(a**3 + (2*a*c*a**2*c + 2*a**2*c*a*c +a*c*a*c*a) + (2*a*c*a*c*a*c) +  c*a**3*c + c*a**2*c*a*c+c*a*c*a**2*c + c*a*c*a*c*a*c)

            cac_sum=0
            for node in range(len(a)):
                cac_sum+=t[node,node]
                assert t[node,node]==t_simple[node,node]

            anet=transforms.aggregate(net,1)
            w,nodes1=anet.get_supra_adjacency_matrix()

            m=ch*a*ch
            saw=m*m*m
            moreno_tot=0
            aw_tot=0
            w_tot=0
            for snode in range(len(w)):
                moreno_sum=0
                aw_sum=0
                for layer in range(int(len(a)/len(w))):
                    aaa,aacac,acaac,acaca,acacac, afa,afcac,acfac,acfca,acfcac=cc.cc_cycle_vector_bf(net,snode,layer)
                    moreno_sum+=aaa+2*aacac+2*acaac+acaca+2*acacac
                    aw_sum+=aaa+aacac+acaac+acaca+acacac
                    
                self.assertEqual(aw_sum,saw[snode+len(w),snode+len(w)]/b/b)
                self.assertEqual(aw_sum,(w*w*w)[snode,snode])
                moreno_tot+=moreno_sum
                aw_tot+=aw_sum
                w_tot+=(w*w*w)[snode,snode]
            self.assertEqual(aw_tot,w_tot)

            """
            print "w0 ", (w*w*w)[0,0]
            s=0
            m=ch*a*ch
            for jt in range(len(w)):
                for kt in range(len(w)):
                    s+=m[0,jt]*m[jt,kt]*m[kt,0]
            print "s0 ",s*16
            print nodes2[0],(m*m*m)[0,0]

            wsum=0
            for node in range(len(w)):
                wsum+=(w*w*w)[node,node]
                print (w*w*w)[node,node]
            #print cac_sum/b/b,wsum
            #print ch*a*ch

            wsum2=0
            node=1
            for i,j in itertools.combinations(anet[node],2):
                wsum+=anet[node][i]*anet[node][j]*anet[i][j]
            """



    def test_weighted_consistency_mslice(self,net):
        anet=transforms.aggregate(net,1)
        onet=transforms.overlay_network(net)
        wmax=max(map(lambda x:x[2],anet.edges))
        owmax=max(map(lambda x:x[2],onet.edges))
        b=len(net.slices[1])

        self.assertAlmostEqual(cc.gcc_contraction_m(net),cc.gcc_contraction_m_ct(net))
        self.assertAlmostEqual(cc.gcc_contraction_m_ct(net),cc.gcc_contraction_m_full(net))
        #self.assertAlmostEqual(cc.gcc_contraction_m_full(net),cc.gcc_super_graph(net))

        self.assertAlmostEqual(cc.gcc_contraction_o2(net),owmax*cc.gcc_zhang(onet)/float(b))
        self.assertAlmostEqual(cc.gcc_contraction_o2(net),cc.gcc_contraction_o_full(net))


        #print "gcc",cc.gcc_contraction_m(net),cc.gcc_contraction_m_ct(net),cc.gcc_contraction_m_full(net),cc.gcc_super_graph(net),cc.gcc_contraction_o2(net),owmax*cc.gcc_zhang(onet)/float(b),cc.gcc_contraction_o(net)

    def test_unweighted_consistency_mslice(self,net):
        self.assertAlmostEqual(cc.gcc_contraction_m_full(net),cc.gcc_super_graph(net))


    def test_consistency_mslice_er(self):
        net=models.er_multilayer(10,5,0.5,randomWeights=True)
        self.test_weighted_consistency_mslice(net)

        net=models.er_multilayer(10,5,0.1,randomWeights=True)
        self.test_weighted_consistency_mslice(net)

        net=models.er_multilayer(10,5,0.5,randomWeights=False)
        self.test_unweighted_consistency_mslice(net)

        net=models.er_multilayer(10,5,0.1,randomWeights=False)
        self.test_unweighted_consistency_mslice(net)

    def test_normalization_full_mslice(self):
        net=models.full_multilayer(5,5)
        self.assertEqual(cc.gcc_contraction_m(net),1.0)
        self.assertEqual(cc.gcc_contraction_m_ct(net),1.0)
        self.assertEqual(cc.gcc_contraction_m_full(net),1.0)
        self.assertEqual(cc.gcc_super_graph(net),1.0)

        self.assertEqual(cc.gcc_contraction_o2(net),1.0)
        self.assertEqual(cc.gcc_contraction_o_full(net),1.0)

        onet=transforms.overlay_network(net)
        owmax=max(map(lambda x:x[2],onet.edges))
        b=len(net.slices[1])
        self.assertEqual(owmax*cc.gcc_zhang(onet)/float(b),1.0)
        self.assertEqual(owmax,b)

        self.assertNotEqual(cc.gcc_contraction_o(net),1.0)


    def test_unweighted_consistency_er(self):
        net=models.er(10,[0.9,0.1])
        net=models.er(10,[0.1,0.3])
        net=models.er(10,[0.4,0.6,0.5,0.3])
        for i in range(1):        
            net=models.er(10,list(map(lambda x:random.random(),range(5))))
            self.test_unweighted_consistency(net)
            self.test_symmetric_aw(net)

        net=pymnet.net.MultiplexNetwork([('categorical',1.0)])
        net[1, 9, 1, 1]=1 
        net[2, 9, 1, 1]=1  
        net[2, 4, 1, 1]=1  
        net[5, 8, 0, 0]=1  
        self.test_unweighted_consistency(net)

        net=pymnet.net.MultiplexNetwork([('categorical',1.0)])
        #net.add_node(1)
        net.add_layer(1)
        net.add_layer(2)
        net.add_layer(3)
        net.add_layer(4)
        net[1,2,1,1]=1
        net[1,3,1,1]=1
        net[2,3,1,1]=1
        self.test_unweighted_consistency(net)

        #net=models.full_multilayer(10,5)
        #self.test_unweighted_consistency(net)

    def test_unweighted_nonglobalnodes_consistency(self,net):
        #Tests direct cycle vector numeration against matrix multiplication
        for snode in net.slices[0]:
            for layer in net.slices[1]:
                self.assertEqual(cc.cc_cycle_vector_adj(net,snode,layer),cc.cc_cycle_vector_bf(net,snode,layer))

        #Test that Barrett clustering coeffiecient is consistent across different versions
        anet=pymnet.transforms.aggregate(net,1)
        for snode in net.slices[0]:
            self.assertEqual(cc.cc_barrett_explicit(net,snode),cc.cc_barrett(net,snode,anet))
            self.assertEqual(cc.cc_barrett_optimized(net,snode,anet),cc.cc_barrett(net,snode,anet))



    def test_unweighted_nonglobalnodes_consistency_er(self):
        net=pymnet.models.er_partially_interconnected([range(10),range(5,15),range(10,20),range(15,25),range(0,25)],[0.5]*5)
        self.test_unweighted_nonglobalnodes_consistency(net)

def test_cc(consistency_tests=False):
    suite = unittest.TestSuite()    
    suite.addTest(TestCC("test_unweighted_flat_triangle"))
    suite.addTest(TestCC("test_unweighted_flat_simple"))
    suite.addTest(TestCC("test_unweighted_mplex_clique"))
    suite.addTest(TestCC("test_unweighted_mplex_simple"))
    suite.addTest(TestCC("test_directed_unweighted"))
    suite.addTest(TestCC("test_unweighted_consistency_er"))
    suite.addTest(TestCC("test_normalization_full_mslice"))
    if consistency_tests:
        suite.addTest(TestCC("test_consistency_mslice_er"))
        suite.addTest(TestCC("test_unweighted_nonglobalnodes_consistency_er"))

    return unittest.TextTestRunner().run(suite).wasSuccessful()


if __name__ == '__main__':
    sys.exit(not test_cc())


