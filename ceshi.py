import numpy

x = numpy.array([5.05, 6.75, 3.21, 2.66])
a = numpy.argsort(-x)
a = numpy.argsort(a)
print a
