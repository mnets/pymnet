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


def test_visuals():
    suite = unittest.TestSuite()    
    suite.addTest(TestVisuals("test_draw_mplex_simple_defaults"))
    suite.addTest(TestVisuals("test_draw_mplex_nonaligned_simple_defaults"))
    suite.addTest(TestVisuals("test_draw_mlayer_example_1d_defaults"))
    suite.addTest(TestVisuals("test_draw_mplex_simple_layer_labels"))
    unittest.TextTestRunner().run(suite) 

if __name__ == '__main__':
    test_visuals()

