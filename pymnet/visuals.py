"""Module for visualizing multilayer networks.
"""

from net import MultiplexNetwork
from io import 

def webplot(net):
    """Create a 3D visualization of a multiplex network for web using D3.
    """
    assert isinstance(net,MultiplexNetwork)
    assert net.aspects==1

    #tobeadded
