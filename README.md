# pymnet: A Python Library for Multilayer Networks

[![codecov](https://codecov.io/gh/mnets/pymnet/graph/badge.svg?token=LI6QBAF7N0)](https://codecov.io/gh/mnets/pymnet)

`pymnet` is a Python package for creating, analyzing, and visualizing multilayer networks as formalized by [Kivelä et al. (2014)](https://doi.org/10.1093/comnet/cnu016).
It is designed for network scientists with an easy-to-use yet flexible interface, featuring, inter alia, representations of a very general class of multilayer networks, structural metrics of multilayer networks, and random multilayer-network models. 

To learn more about the concepts and design principles underlying `pymnet`, check out [this overview](https://mnets.github.io/pymnet/overview.html).

## Features

* Written in pure Python
* Full support for general [multilayer networks](http://comnet.oxfordjournals.org/content/2/3/203)
* Efficient handling of multiplex networks (with automatically generated lazy evaluation of coupling edges)
* Extensive functionality –– analysis, transformations, reading and writing networks, network models, etc.
* Flexible multilayer-network visualization (using Matplotlib and D3)
* Integration with [NetworkX](https://networkx.org/) for monoplex network analysis

## Working with pymnet

### Installation
We recommend executing the following command in a virtual environment: 
```console
$ python -m pip install pymnet
```

### Usage
To get started with `pymnet`, check out our [tutorials](https://mnets.github.io/pymnet/tutorials) –– and when in doubt, consult the [API reference](https://mnets.github.io/pymnet/reference.html) contained in our [documentation](https://mnets.github.io/pymnet/).

As an introductory example, with the following code, we can create a small multiplex network capturing different types of social relations between individuals and visualize the result:

```python
import pymnet

net_social = pymnet.MultiplexNetwork(couplings="categorical", fullyInterconnected=False)
net_social["Alice", "Bob", "Friends"] = 1
net_social["Alice", "Carol", "Friends"] = 1
net_social["Bob", "Carol", "Friends"] = 1
net_social["Alice", "Bob", "Married"] = 1

fig_social = pymnet.draw(net_social, layout="circular", layerPadding=0.2, defaultLayerLabelLoc=(0.9,0.9))
```

<p align="center" style="margin-top:-6rem;margin-bottom:-3rem">
    <img alt="An image of a small multiplex social network." width="60%" src="https://github.com/mnets/pymnet/raw/master/socialnet.png"> 
</p>


## Contributing

We welcome contributions!
Before you get started, please check out our [contribution guide](CONTRIBUTING.md).

## Asking Questions

* For bugs, feature requests, etc., please use [GitHub issues][github-issues].
* Otherwise, feel free to contact the main developer: [Mikko Kivelä](http://www.mkivela.com/)

[github-issues]: https://github.com/mnets/pymnet/issues
