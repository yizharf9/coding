import numpy as np

# np.random.seed(16)
A = np.random.randint(0,51,40)
B = sorted(A[:len(A)//2])
A = sorted(A[len(A)//2:])

print(f"A : {A}")
print(f"B : {B}")

def bin_search(A,a):
    return bin_search_recurse(A,a,len(A)//2)

def bin_search_recurse(A,a,idx):
    print(f"A[idx],idx : {A[idx],idx}")
    print(f"A : {A}\n")
    
    if a == A[idx]:
        print(f"found {a} at index {idx}")
        return idx
    
    if len(A) == 1 or idx == 0 :
        print(f"didn't find {a}, found {A[idx]} instead!")
        if a != A[idx]:
            return -1
    
    elif a > A[idx]:
        relative_idx = bin_search_recurse(A[idx:],a,idx//2)
        return idx + relative_idx if relative_idx != -1 else -1
    elif a < A[idx]:
        relative_idx = bin_search_recurse(A[:idx],a,idx//2)
        return relative_idx if relative_idx != -1 else -1

def bin_search_testing():
    searched_element = 15
    # searched_element = A[3*(len(A)//4)]
    result = bin_search(A,searched_element)
    print(f"result : {result}")
    try:
        searched_index = A.index(searched_element)
        print(f"solution : {searched_index}")
    except:
        print(f"solution : {searched_element} not in list!")