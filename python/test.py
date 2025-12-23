import numpy as np 

A = np.array(
    [
        [8,3],
        [0,9],
    ]
)
B = np.array(
    [
        [1,9],
        [8,6],
    ]
)
print(A.T@ B)
print(np.trace(A.T@B))

