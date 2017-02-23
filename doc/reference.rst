.. _reference:

Reference
=========
.. automodule:: pymnet
.. autosummary::
  :toctree: autogen

Data structures
---------------
.. automodule:: pymnet.net
.. autosummary::
  :toctree: autogen

.. automodule:: pymnet
.. autosummary::
  :toctree: autogen

  MultilayerNetwork
  MultiplexNetwork
  MultilayerNode

Network models
--------------
.. automodule:: pymnet.models
.. autosummary::
  :toctree: autogen

.. automodule:: pymnet
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

.. automodule:: pymnet
.. autosummary::
  :toctree: autogen
   
  aggregate
  subnet
  supra_adjacency_matrix

Reading and Writing Networks
----------------------------
.. automodule:: pymnet.io
.. autosummary::
  :toctree: autogen

.. automodule:: pymnet
.. autosummary::
  :toctree: autogen

  read_ucinet

Basic Network Diagnostics
-------------------------
.. automodule:: pymnet.diagnostics
.. autosummary::
  :toctree: autogen

.. automodule:: pymnet
.. autosummary::
  :toctree: autogen

  degs
  density
  multiplex_degs
  multiplex_density

Clustering coefficients
-----------------------
.. automodule:: pymnet.cc
.. autosummary::
  :toctree: autogen

.. automodule:: pymnet
.. autosummary::
  :toctree: autogen

  lcc
  cc_zhang
  gcc_zhang
  cc_onnela
  cc_barrat
  cc_barrett
  lcc_brodka
  cc_sequence  
  lcc_aw
  avg_lcc_aw
  gcc_aw
  sncc_aw
  elementary_cycles


Visualization
-------------
.. automodule:: pymnet.visuals
.. autosummary::
  :toctree: autogen

.. automodule:: pymnet
.. autosummary::
  :toctree: autogen

  draw
  webplot

Isomorphisms
------------
.. automodule:: pymnet.isomorphisms
.. autosummary::
  :toctree: autogen

.. automodule:: pymnet
.. autosummary::
  :toctree: autogen

  is_isomorphic
  get_complete_invariant
  get_automorphism_generators
  get_isomorphism

