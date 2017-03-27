import unittest
from operator import itemgetter
import sys

import random
from pymnet import net,transforms,models,isomorphisms

def random_relabel(net,relabel_aspects):
    """Randomly relabel some aspects of the input network.
    """
    labelings=[]
    for a in range(net.aspects+1):
        if a in relabel_aspects:
            elayers=list(net.slices[a])
            random.shuffle(elayers)
            labeling=dict([(k,i) for i,k in enumerate(elayers)])
            labelings.append(labeling)
        else:
            labelings.append({})

    if net.aspects>=1:
        return transforms.relabel(net,nodeNames=labelings[0],layerNames=labelings[1:])
    else:
        return transforms.relabel(net,nodeNames=labelings[0])




class TestIsomorphisms(unittest.TestCase):
    
    def setUp(self):
        pass


    def is_isomorphic_multimethod(self,net1,net2,allowed_aspects,backend):        
        """This is a helper function that tries to use as many of the cababilities
        of the backend to test the isomorphism, and makes sure that the results 
        are consistent.
        """
        #Calculate the results in various ways
        results={}
        if backend in isomorphisms.comparison_backends:
            results["comparison"]=isomorphisms.is_isomorphic(net1,net2,allowed_aspects=allowed_aspects,backend=backend)
        if backend in isomorphisms.complete_invariant_backends:
            c1=isomorphisms.get_complete_invariant(net1,allowed_aspects=allowed_aspects,backend=backend)
            c2=isomorphisms.get_complete_invariant(net2,allowed_aspects=allowed_aspects,backend=backend)
            results["complete_invariant"]=(c1==c2)

        #Check that there was at least one way to get the result
        self.assertTrue(len(results)>0) #This backend doesn't do anything...

        #Check that the results are consistent
        #all_same= (len(set(results.values()))==1)
        all_same= (len(set(  (results[k] for k in results)  ))==1)
        self.assertTrue(all_same)

        #return results.values()[0]
        return [results[k] for k in results][0]

    def test_comparison_simple_mlayer(self,backend="nx"):
        """This tests that the simple example given in the article M. Kivela & M.A. Porter 
        "Isomorphisms in Multilayer Networks", Figure 2, works.
        """
        
        neta=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        neta.add_layer("X")
        neta.add_layer("Y")
        neta[1,"X"][2,"X"]=1
        neta[3,"X"][3,"Y"]=1
        neta[2,"Y"][3,"Y"]=1

        netb=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        netb.add_layer("X")
        netb.add_layer("Y")
        netb[2,"X"][3,"X"]=1
        netb[1,"X"][1,"Y"]=1
        netb[1,"Y"][3,"Y"]=1

        netc=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        netc.add_layer("X")
        netc.add_layer("Y")
        netc[1,"Y"][2,"Y"]=1
        netc[3,"Y"][3,"X"]=1
        netc[2,"X"][3,"X"]=1

        netd=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        netd.add_layer("X")
        netd.add_layer("Y")
        netd[2,"Y"][3,"Y"]=1
        netd[1,"Y"][1,"X"]=1
        netd[3,"X"][1,"X"]=1

        #Building an auxiliary graph, but no testing yet
        isomorphisms.nxbackend.AuxiliaryGraphBuilderNX(neta,[0])
        isomorphisms.nxbackend.AuxiliaryGraphBuilderNX(netc,[0])

        #Network a Isomorphic to itself
        self.assertTrue(self.is_isomorphic_multimethod(neta,neta,allowed_aspects=[],backend=backend))
        self.assertTrue(self.is_isomorphic_multimethod(neta,neta,allowed_aspects=[0],backend=backend))
        self.assertTrue(self.is_isomorphic_multimethod(neta,neta,allowed_aspects=[1],backend=backend))
        self.assertTrue(self.is_isomorphic_multimethod(neta,neta,allowed_aspects=[0,1],backend=backend))

        #Network a vertex-isomorphic to network b
        self.assertTrue(self.is_isomorphic_multimethod(neta,netb,allowed_aspects=[0],backend=backend))

        #Network a layer-isomorphic to network c
        self.assertTrue(self.is_isomorphic_multimethod(neta,netc,allowed_aspects=[1],backend=backend))

        #Network a vertex-layer-isomorphic to network d
        self.assertTrue(self.is_isomorphic_multimethod(neta,netd,allowed_aspects=[0,1],backend=backend))

        #Network a is not vertex-isomorphic to network c or d
        self.assertFalse(self.is_isomorphic_multimethod(neta,netc,allowed_aspects=[0],backend=backend))
        self.assertFalse(self.is_isomorphic_multimethod(neta,netd,allowed_aspects=[0],backend=backend))

        #Network a is not layer-isomorphic to network b or d
        self.assertFalse(self.is_isomorphic_multimethod(neta,netb,allowed_aspects=[1],backend=backend))
        self.assertFalse(self.is_isomorphic_multimethod(neta,netd,allowed_aspects=[1],backend=backend))

        #Network a is vertex-layer-isomorphic to network b or c
        self.assertTrue(self.is_isomorphic_multimethod(neta,netb,allowed_aspects=[0,1],backend=backend))
        self.assertTrue(self.is_isomorphic_multimethod(neta,netc,allowed_aspects=[0,1],backend=backend))


    def _comparison_multiplex_category_counts(self,nodes,layers,aspects,backend="nx"):
        fullnet=models.full(nodes,layers,couplings=None)
        classes=[]
        for net in transforms.subnet_iter(fullnet,remove_edges=True):
            newtype=True
            for oldnet in classes:
                if self.is_isomorphic_multimethod(net,oldnet,allowed_aspects=aspects,backend=backend):
                    newtype=False
            if newtype:
                classes.append(net)
        return len(classes)


    def test_comparison_multiplex_category_counts_fast(self,backend="nx"):
        """Test that the number of isomorphism categories are correct for small multiplex networks.

        Note that using the comparison (instead of certificates) for category count is slow.
        """
        #These results are from the Table I in the article "Isomorphisms in Multilayer Networks"
        self.assertEqual(self._comparison_multiplex_category_counts(2,1,[0],backend=backend),2)
        self.assertEqual(self._comparison_multiplex_category_counts(3,1,[0],backend=backend),4)
        self.assertEqual(self._comparison_multiplex_category_counts(4,1,[0],backend=backend),11)

        self.assertEqual(self._comparison_multiplex_category_counts(2,2,[0],backend=backend),4)
        self.assertEqual(self._comparison_multiplex_category_counts(3,2,[0],backend=backend),20)

        self.assertEqual(self._comparison_multiplex_category_counts(2,3,[0],backend=backend),8)
        #self.assertEqual(self._comparison_multiplex_category_counts(3,3,[0],backend=backend),120) #slow

        self.assertEqual(self._comparison_multiplex_category_counts(2,2,[0,1],backend=backend),3)
        self.assertEqual(self._comparison_multiplex_category_counts(3,2,[0,1],backend=backend),13)
        #self.assertEqual(self._comparison_multiplex_category_counts(3,3,[0,1],backend=backend),36) #slow

        self.assertEqual(self._comparison_multiplex_category_counts(2,3,[0,1],backend=backend),4)


    def test_comparison_random_relabel_mplex_single_aspect_fast(self,backend="nx"):
        """Test that multiplex networks are isomorphic to randomly relabeled ones.
        
        Single aspect version.
        """

        nnodes=[4]
        nlayers=[4]
        ps=[0.5]
        repeats=5
        for nodes in nnodes:
            for layers in nlayers:
                for p in ps:
                    for r in range(repeats):
                        net=models.er(nodes,layers*[p])
                        
                        #node isomorphism
                        self._test_comparison_random_relabel(net,[0],backend)

                        #layer isomorphism
                        self._test_comparison_random_relabel(net,[1],backend)

                        #node-layer isomorphism
                        self._test_comparison_random_relabel(net,[0,1],backend)


    def _test_comparison_random_relabel(self,net,aspects,backend):
        net2=random_relabel(net,aspects)
        self.assertTrue(self.is_isomorphic_multimethod(net,net2,allowed_aspects=aspects,backend=backend))
        #net2[net2.edges.__iter__().next()[:-1]]=net2.noEdge #remove an arbitrary edge
        #self.assertFalse(self.is_isomorphic_multimethod(net,net2,allowed_aspects=aspects,backend=backend))


    def test_comparison_random_relabel_mlayer_single_aspect_fast(self,backend="nx"):
        """Test that multilayer networks are isomorphic to randomly relabeled ones.
        
        Single aspect version.
        """
        nnodes=[10]
        nlayers=[4]
        ps=[0.5]
        repeats=5
        for nodes in nnodes:
            for layers in nlayers:
                for p in ps:
                    for r in range(repeats):
                        net=models.er_multilayer(nodes,layers,p)
                        
                        #node isomorphism
                        self._test_comparison_random_relabel(net,[0],backend)

                        #layer isomorphism
                        self._test_comparison_random_relabel(net,[1],backend)

                        #node-layer isomorphism
                        self._test_comparison_random_relabel(net,[0,1],backend)

                        if r>0: #should be very unlikely that the previous network is isomorphic
                            self.assertFalse(self.is_isomorphic_multimethod(net,prevnet,allowed_aspects=[0],backend=backend))
                            self.assertFalse(self.is_isomorphic_multimethod(net,prevnet,allowed_aspects=[1],backend=backend))
                            self.assertFalse(self.is_isomorphic_multimethod(net,prevnet,allowed_aspects=[0,1],backend=backend))
                        prevnet=net



    ## NX tests
    def test_comparison_random_relabel_mplex_single_aspect_fast_nx(self):
        self.test_comparison_random_relabel_mplex_single_aspect_fast(backend="nx")
    def test_comparison_random_relabel_mlayer_single_aspect_fast_nx(self):
        self.test_comparison_random_relabel_mlayer_single_aspect_fast(backend="nx")
    def test_comparison_simple_mlayer_nx(self):
        self.test_comparison_simple_mlayer(backend="nx")
    def test_comparison_multiplex_category_counts_fast_nx(self):
        self.test_comparison_multiplex_category_counts_fast(backend="nx")


    ## Bliss tests
    def test_comparison_random_relabel_mplex_single_aspect_fast_bliss(self):
        self.test_comparison_random_relabel_mplex_single_aspect_fast(backend="bliss")
    def test_comparison_random_relabel_mlayer_single_aspect_fast_bliss(self):
        self.test_comparison_random_relabel_mlayer_single_aspect_fast(backend="bliss")
    def test_comparison_simple_mlayer_bliss(self):
        self.test_comparison_simple_mlayer(backend="bliss")
    def test_comparison_multiplex_category_counts_fast_bliss(self):
        self.test_comparison_multiplex_category_counts_fast(backend="bliss")

def test_isomorphisms():
    suite = unittest.TestSuite()   
    if "nx" in isomorphisms.comparison_backends:
        suite.addTest(TestIsomorphisms("test_comparison_simple_mlayer_nx"))
        suite.addTest(TestIsomorphisms("test_comparison_random_relabel_mlayer_single_aspect_fast_nx"))
        suite.addTest(TestIsomorphisms("test_comparison_random_relabel_mplex_single_aspect_fast_nx"))
        suite.addTest(TestIsomorphisms("test_comparison_multiplex_category_counts_fast_nx"))

    if "bliss" in isomorphisms.comparison_backends:
        suite.addTest(TestIsomorphisms("test_comparison_simple_mlayer_bliss"))
        suite.addTest(TestIsomorphisms("test_comparison_random_relabel_mlayer_single_aspect_fast_bliss"))
        suite.addTest(TestIsomorphisms("test_comparison_random_relabel_mplex_single_aspect_fast_bliss"))
        suite.addTest(TestIsomorphisms("test_comparison_multiplex_category_counts_fast_bliss"))


    return unittest.TextTestRunner().run(suite).wasSuccessful() 

if __name__ == '__main__':
    sys.exit(not test_isomorphisms())

