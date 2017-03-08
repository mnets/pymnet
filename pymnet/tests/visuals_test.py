import unittest
from operator import itemgetter

import sys,os
sys.path.append("../../")
from pymnet import net,visuals


class TestVisuals(unittest.TestCase):
    figdirname="figs"
    
    def setUp(self):
        #create directory for figs if it doesn't exist
        self.figdirpath=os.path.join(os.path.dirname(os.path.realpath(__file__)),self.figdirname)
        if not os.path.exists(self.figdirpath):
            os.mkdir(self.figdirpath)

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

        self.mplex_simple=n

        n=net.MultiplexNetwork([('categorical',1.0)],fullyInterconnected=False)

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

        self.mplex_nonaligned_simple=n

        #The 2-aspect example network for the review article
        n=net.MultilayerNetwork(aspects=2,fullyInterconnected=False)
        n[1,2,'A','A','X','X']=1
        n[2,3,'A','A','Y','Y']=1
        n[1,3,'B','B','X','X']=1
        n[1,4,'B','B','X','X']=1
        n[3,4,'B','B','X','X']=1
        n[1,1,'A','B','X','X']=1
        n[1,4,'A','B','X','X']=1
        n[1,1,'B','B','X','Y']=1
        n[3,3,'A','A','X','Y']=1
        n[3,4,'A','B','X','Y']=1
        self.mlayer_example_2d=n

        n=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        n[1,2,'A','A']=1
        n[2,3,'A','A']=1
        n[1,3,'B','B']=1
        n[1,4,'B','B']=1
        n[3,4,'B','B']=1
        n[1,1,'A','B']=1
        n[1,4,'A','B']=1
        n[3,4,'A','B']=1
        self.mlayer_example_1d=n

        #Non-aligned network for testing multilayer coordinates
        n=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        n.add_node(0,'a')
        n.add_node(1,'b')
        n.add_node(2,'b')
        n.add_node(3,'b')
        n.add_node(4,'b')
        n.add_node(5,'b')
        n[1,2,'b','b']=1
        n[2,3,'b','b']=1
        n[3,4,'b','b']=1
        n[4,1,'b','b']=1

        n[0,5,'a','b']=1
        n[1,5,'b','b']=1
        n[2,5,'b','b']=1
        n[3,5,'b','b']=1
        n[4,5,'b','b']=1
        self.mlayer_nonaligned_aligntest=n

        #Second non-aligned network for testing multilayer coordinates
        n=net.MultilayerNetwork(aspects=1,fullyInterconnected=False)
        n.add_node(0,'a')
        n.add_node(1,'b')
        n.add_node(2,'b')
        n.add_node(3,'b')
        n.add_node(4,'b')

        n[1,2,'b','b']=1
        n[2,3,'b','b']=1
        n[3,4,'b','b']=1
        n[4,1,'b','b']=1

        n[0,0,'a','b']=1
        n[1,0,'b','b']=1
        n[2,0,'b','b']=1
        n[3,0,'b','b']=1
        n[4,0,'b','b']=1
        self.mlayer_nonaligned_aligntest2=n


        n=net.MultilayerNetwork(aspects=0,fullyInterconnected=True)
        n[1,2]=1
        n[2,3]=1
        n[1,3]=1
        n[1,4]=2
        n[3,4]=2
        self.mlayer_example_monoplex=n

    def test_draw_mplex_simple_defaults(self):
        fig=visuals.draw(self.mplex_simple)
        fig.savefig(os.path.join(self.figdirpath,"mplex_simple_defaults.png"))

    def test_draw_mplex_nonaligned_simple_defaults(self):
        fig=visuals.draw(self.mplex_nonaligned_simple)
        fig.savefig(os.path.join(self.figdirpath,"mplex_nonaligned_simple_defaults.png"))

    def test_draw_mlayer_example_1d_defaults(self):
        fig=visuals.draw(self.mlayer_example_1d)
        fig.savefig(os.path.join(self.figdirpath,"mlayer_example_1d_defaults.png"))

    def test_draw_mplex_simple_layer_labels(self):
        fig=visuals.draw(self.mplex_simple,layerLabelColorDict={1:"blue",2:"green"},layerLabelSizeRule={"rule":"name","scaleby":10},layerLabelAlphaDict={3:0.5},layerLabelStyleDict={2:"italic"})
        fig.savefig(os.path.join(self.figdirpath,"mlayer_example_1d_layer_labels.png"))

    def test_draw_mlayer_nonaligned_mlayer_coords(self):
        nc=visuals.layouts.get_fruchterman_reingold_multilayer_layout(self.mlayer_nonaligned_aligntest)
        fig=visuals.draw(self.mlayer_nonaligned_aligntest,nodeCoords=nc)
        fig.savefig(os.path.join(self.figdirpath,"mlayer_nonaligned_mlayer_coords.png"))

        nc2=visuals.layouts.get_fruchterman_reingold_multilayer_layout(self.mlayer_nonaligned_aligntest2)
        fig2=visuals.draw(self.mlayer_nonaligned_aligntest2,nodeCoords=nc2)
        fig2.savefig(os.path.join(self.figdirpath,"mlayer_nonaligned_mlayer_coords2.png"))

        nc3=visuals.layouts.get_fruchterman_reingold_multilayer_layout(self.mlayer_nonaligned_aligntest2,alignedNodes=False)
        fig3=visuals.draw(self.mlayer_nonaligned_aligntest2,nodelayerCoords=nc3)
        fig3.savefig(os.path.join(self.figdirpath,"mlayer_nonaligned_mlayer_coords3.png"))



def test_visuals():
    suite = unittest.TestSuite()    
    suite.addTest(TestVisuals("test_draw_mplex_simple_defaults"))
    suite.addTest(TestVisuals("test_draw_mplex_nonaligned_simple_defaults"))
    suite.addTest(TestVisuals("test_draw_mlayer_example_1d_defaults"))
    suite.addTest(TestVisuals("test_draw_mplex_simple_layer_labels"))
    suite.addTest(TestVisuals("test_draw_mlayer_nonaligned_mlayer_coords"))
    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_visuals()

