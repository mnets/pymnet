Reference
=========
  

Data structures
---------------
.. automodule:: pymnet.net
.. autosummary::
  :toctree: autogen

  MultilayerNetwork
  MultiplexNetwork


Network models
--------------
.. automodule:: pymnet.models
.. autosummary::
  :toctree: autogen

  er
  conf
  single_layer_er
  single_layer_conf
  er_partially_interconnected
  full
  full_multilayer
  er_multilayer

Transforming Networks
---------------------
.. automodule:: pymnet.transforms
.. autosummary::
  :toctree: autogen
   
  aggregate
  overlay_network
  subnet

Reading and Writing Networks
----------------------------
.. automodule:: pymnet.io
.. autosummary::
  :toctree: autogen

  read_ucinet

Basic Network Diagnostics
-------------------------
.. automodule:: pymnet.diagnostics
.. autosummary::
  :toctree: autogen

  monoplex_degs

Clustering coefficients
-----------------------
.. automodule:: pymnet.cc
.. autosummary::
  :toctree: autogen

  cc
  cc_zhang
  gcc_zhang
  cc_onnela
  cc_barrat
  cc_barrett
  cc_sequence  
  lcc_alternating_walks
  avg_lcc_alternating_walks
  gcc_alternating_walks_seplayers
  sncc_alternating_walks
  sncc_alternating_walks_seplayers
