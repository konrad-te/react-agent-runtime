import numpy 

first_input = list(map(int, input().split()))
second_input = list(map(int, input().split()))

A = numpy.array(first_input)
B = numpy.array(second_input)

print(numpy.inner(A,B))
print(numpy.outer(A,B))