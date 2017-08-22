from .net_test import test_net
from .cc_test import test_cc
from .diagnostics_test import test_diagnostics
from .io_test import test_io
from .models_test import test_models
from .transforms_test import test_transforms
from .visuals_test import test_visuals
from .isomorphisms_test import test_isomorphisms
from .sampling_test import test_sampling

try:
    import networkx
    from .nxwrap_test import test_nxwrap
    nximported=True
except ImportError:
    nximported=False

def test_all():
    codes=[]
    codes.append(test_net())
    codes.append(test_cc())
    codes.append(test_diagnostics())
    codes.append(test_io())
    codes.append(test_models())
    codes.append(test_transforms())
    codes.append(test_visuals())
    codes.append(test_isomorphisms())
    codes.append(test_sampling())
    if nximported: codes.append(test_nxwrap())
    return all(codes)
