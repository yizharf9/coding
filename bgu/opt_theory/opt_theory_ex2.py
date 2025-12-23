import scipy
import numpy as np

id1 = [2,0,8,0,6,6,3,8,1]

c = [1,-0.5,0,0,0]

A = [
    [1,2,3,4,5,6,7,8]
]

b = [9]

variance = 1
eps = np.random.randn(len(id1)) * variance
x = np.array(id1) + eps

print(f"id1 : {id1}")
print(f"A : {A}")
print(f"b : {b}")
print(f"eps : {eps}")
print(f"x : {x}")
bounds = [
    (0,None),
    (0,None),
    (0,None),
    (0,None),
    (0,None),
]

x_star = scipy.optimize.linprog(c,A,b, bounds =  bounds , method = "highs")

"""
this yields the output : 
...
fun: -0.5
x: [ 0.000e+00  1.000e+00  0.000e+00  0.000e+00  0.000e+00]
...

meaning we reached the solution that we found in previous sections : 
solution            : x = [0,1] 
with cost value     : f(x) = -1/2
"""
print(x_star)
