import random
import math
# class Node():
#     def __init__(self, value, left=None, right=None):
#         self.value = value
#         self.left = left
#         self.right = right

# def inorder(root):
#     if root.right is None and root.left is None:
#         print(f"leaf : {root.value[0]} (Freq: {root.value[1]})")
#         return

#     if root.left is not None:
#         inorder(root.left)
#     if root.right is not None :
#         inorder(root.right)



def opt_solution_1(A):
    """dynamic programming
    given an array of positive integers A = [a1...an]
    return a partition of the array as partition indices 
    such that the sum of the products of the partition is maximal.
    alg. should run in O(N^2) time.

    Args:
        A (list[int]): array of positive integers

    Returns:
        P ([list[int]]): array of partition indices
        max (int): sum of products of the partition
    """
    N = len(A)
    DP = [0] * ( N + 1)
    indices = [0] * ( N + 1)
    
    
    for i in range(1,N+1):
        DP_max = -float("inf")
        p_curr = 1
        val = 0
        for j in range(i,0,-1):
            
            p_curr *= A[j-1]
            val = DP[j-1] + p_curr
            
            if DP_max < val :
                DP_max = val
                indices[i] = j
                
        DP[i] = DP_max
    
    partition = []
    idx_curr = N
    while idx_curr > 0 :
        start = indices[idx_curr]
        partition.append(A[start-1:idx_curr])
        idx_curr = start - 1
    
    return DP[N],partition[::-1]

def i_j_maxdist(A,p_flag = False):
    """
    - for a given array of integers A = [a1...an]
    
    - return the largest distance in the array a_i - a_j  s.t. i<j 
    
    - algorithm should do so in O(N) time.
    """
    N = len(A)
    current_max = 0 
    a_max = 0
    a_min = 0
    
    for i in range(N):
        if A[i] > A[a_max] :
            a_max = i
            a_min = i
            current_max = A[a_max] - A[a_min]
            
        if A[i] < A[a_min] :
            a_min = i
            current_max = A[a_max] - A[a_min]
        
        if p_flag:
            print(A)
            print(f"A[a_max] : {A[a_max]}")
            print(f"A[a_min] : {A[a_min]}")
            print(f"current_max : {current_max}\n")
        
    return a_max,a_min,current_max
    
if __name__ == "__main__":
    N = 10 
    # random.seed(42)
    A = [abs(math.floor(random.normalvariate(mu=0,sigma=N))) for i in range(N)]
    
    sequence = [2, 3, 0.5, 4] # Using some floats to show variety, though problem says integers
    # If input is [1, 2, 1, 3]
    sequence = [1, 2, 1, 3]
    max_sum , partition = opt_solution_1(A)

    print(f"A: {A}")
    print(f"max_sum: {max_sum}")
    print(f"partition: {partition}")
    
