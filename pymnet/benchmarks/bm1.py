from pymnet import *
from timeit import Timer

### ER with large number of layers

def create_er():
    net=er(10,10**5*[0.1])
    return net

timer=Timer(create_er)
result=timer.timeit(number=100)


### ER with large number of nodes

def create_er2():
    net=er(10**5,10*[10**-5])
    return net

timer2=Timer(create_er2)
result2=timer2.timeit(number=100)


### Aggregating ER

net=er(10**5,10*[10**-5])

def aggr():
    aggregate(net,1)

timer3=Timer(aggr)
result3=timer3.timeit(number=100)


print result,result2,result3
