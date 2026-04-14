import random
import math
import matplotlib.pyplot as plt
import numpy as np
import time
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
    
def min_2d_distance(A):
    """
    - for a given array of point in 2d plane A = [p1 = (x1,y1)...pn]
    
    - return the smallest distance in the array 
    
    - algorithm should do so in O(N*log(N)) time.
    """
    if len(A) <= 1:
        return float("inf")
    if len(A) == 2:
        x1, y1 = A[0]
        x2, y2 = A[1]
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    
    median = len(A) // 2
    mid_x = A[median][0]  # We need to explicitly capture the X-coordinate of our dividing line
    
    d_L = min_2d_distance(A[:median])
    d_R = min_2d_distance(A[median:])
    
    d = min(d_L, d_R)  # This is our delta (δ)!
    
    # Step 1: Build the boundary strip (Filter out points too far from mid_x)
    strip = [p for p in A if abs(p[0] - mid_x) < d]
    
    # Step 2: Sort the boundary strip purely by Y
    strip.sort(key=lambda p: p[1])
    
    # Step 3: Iterate through the Y-sorted strip
    for i in range(len(strip)):
        # Look ahead at the subsequent points...
        for j in range(i + 1, len(strip)):
            
            # THE MAGIC BREAK CONDITION:
            # If the Y-distance exceeds 'd', stop checking for point 'i'!
            # Mathematical packing guarantees this 'break' hits within 7 loops.
            if strip[j][1] - strip[i][1] >= d:
                break
                
            # If it's within the safe Y-distance, check the true 2D Euclidean distance
            x1, y1 = strip[i]
            x2, y2 = strip[j]
            dist = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
            
            # If we found a closer pair, update our delta!
            if dist < d:
                d = dist
                
    return d
            
def visualize_time_complexity():
    # Different sizes of N to test
    ns = [100, 500, 1000, 2000, 5000, 10000, 20000, 30000, 40000, 50000]
    times = []

    print("Running tests... This may take a few seconds.")
    for n in ns:
        # Generate N random coordinates in a 100,000 x 100,000 grid
        A = [(random.uniform(0, 100000), random.uniform(0, 100000)) for _ in range(n)]
        
        # PRE-SORT by X coordinate (as our function expects)
        A.sort(key=lambda p: p[0])
        
        # Start the clock
        start_time = time.perf_counter()
        min_2d_distance(A)
        end_time = time.perf_counter()
        
        # Record the elapsed time
        elapsed = end_time - start_time
        times.append(elapsed)
        print(f"N = {n:5d} | Time = {elapsed:.4f} seconds")

    # Generate the Matplotlib Graph
    plt.plot(ns, times, marker='o', linestyle='-', color='#2ca02c', linewidth=2, markersize=6)
    plt.title('Runtime of Closest Pair of Points ($O(N \log^2 N)$)')
    plt.xlabel('Number of Points ($N$)')
    plt.ylabel('Execution Time (seconds)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def lumberjacks(C:list[int],L:int):
    C = [0] + C + [L]
    print(f"C : {C}")
    
    N = len(C)
    DP = [[0]*N for i in range(N)]
    
    for length in range(2,N):
        for i in range(N-length):
            
            j = i + length
            DP[i][j] = float("inf")
            
            for k in range(i+1,j):
                current_val = C[j] - C[i] + DP[i][k] + DP[k][j]
                DP[i][j] = current_val if current_val < DP[i][j] else current_val
    return DP,DP[0][N-1]
    
if __name__ == "__main__":
    L = 20
    K = 5
    p = 0.2
    C = [i for i in range(1,L) if random.random() < p]
    solution = lumberjacks(C,L)
    print(f"solution : {solution[1]}")
    print(f"DP : ")
    for line in solution[0]:
        print(line)