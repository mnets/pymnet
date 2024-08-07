``pymnet``: A Multilayer-Networks Library for Python
====================================================

.. toctree::
   :maxdepth: 2
   :hidden:

   overview
   tutorials
   reference

.. sidebar:: Multilayer networks
    
   .. figure:: index-example.png      
       :height: 250 pt
       :align: left

   The library is based on the general definition of **multilayer networks** presented in a `review article <http://arxiv.org/abs/1309.7233>`_. Multilayer networks can be used to represent various types network generalizations found in the literature. For example, multiplex networks, temporal networks, networks of networks, and interdependent networks are all types of multilayer networks. The library supports even more general types of networks with multiple *aspects* such that the networks can for example have both temporal and multiplex aspect at the same time. 

   The visualization on the left is produced with the library. See the visualization tutorial for instructions on how to visualize your own network data with the library!


``pymnet`` is a free library for analyzing multilayer networks.
The easiest way to get ``pymnet`` is via pip:

.. code-block:: bash

    $ pip install pymnet


**Main features include:**

* Pure Python implementation

* Can handle general multilayer networks

* Data structures for multilayer networks and multiplex networks 

* Scalable implementation for sparse networks: memory usage scales linearly with the number of edges and number of nodes

* Rule-based generation and lazy evaluation of coupling edges

* Various network analysis methods, transformations, reading and writing networks, network models, etc.

* Visualization (using matplotlib or D3 as a backend)

* Integration with NetworkX for monoplex network analysis



**Documentation:**


* :ref:`overview`: *Overview of the design of the library and benchmarks* 
* :ref:`reference`: *Reference for all functions and classes in the library* 
* :ref:`tutorials`: *Easy way of getting started with various topics*


