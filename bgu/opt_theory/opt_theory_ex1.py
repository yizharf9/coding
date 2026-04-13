import scipy
import numpy as np

# c = [1,-0.5,0,0,0]
c = [1,1,-1,0,0]

# A = [
#     [1,1,1,0,0],
#     [0,0,0,1,0],
#     [0,1,0,0,1],
# ]
A = [
    [1,0,1,-1,0],
    [0,1,-1,0,-1]
]

# b = [1,3,2]
b = [1,1]

# bounds = [
#     (0,None),
#     (0,None),
#     (0,None),
#     (0,None),
#     (0,None),
# ]
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
fun: -0.5di
x: [ 0.000e+00  1.000e+00  0.000e+00  0.000e+00  0.000e+00]
...

meaning we reached the solution that we found in previous sections : 
solution            : x = [0,1] 
with cost value     : f(x) = -1/2
"""
print(x_star)
