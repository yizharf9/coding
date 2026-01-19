import numpy as np
import cvxpy as cp
import time

def generate_symmetric_psd_matrix(n):
    """
    Generates a random Symmetric Positive Semidefinite (PSD) matrix W.
    According to the problem W must be in S+^n.
    We generate a uniform random symmetric matrix and shift eigenvalues to be non-negative.
    """
    # Generate uniform random values for the lower triangle
    A = np.random.rand(n, n)
    # Symmetrize: Lower triangle + Upper triangle (excluding diagonal to avoid double counting)
    W = np.tril(A) + np.tril(A, -1).T
    
    # Enforce Positive Semidefinite (PSD) property:
    # Shift eigenvalues so the smallest is >= 0
    min_eig = np.min(np.linalg.eigvalsh(W))
    if min_eig < 0:
        W = W + (abs(min_eig) + 1e-5) * np.eye(n)
        
    return W

def solve_spectral_relaxation(W, n):
    """
    Solves the Spectral Relaxation.
    Max x.T * W * x s.t. ||x||^2 = n
    Solution is n * lambda_max(W).
    """
    start_time = time.time()
    
    # Compute eigenvalues and eigenvectors
    # eigh is optimized for symmetric/Hermitian matrices
    evals, evecs = np.linalg.eigh(W)
    
    # Get the largest eigenvalue
    max_eval = np.max(evals)
    
    # The upper bound is n * lambda_max
    upper_bound = n * max_eval
    
    return upper_bound, time.time() - start_time

def solve_sdp_dual(W, n):
    """
    Solves the Dual of the SDP Relaxation.
    Min sum(gamma) s.t. diag(gamma) - W >= 0
    """
    # Variable: gamma is a vector of size n
    gamma = cp.Variable(n)
    
    # Constraint: diag(gamma) - W must be Positive Semidefinite
    # We construct the matrix explicitly:
    mat_constraint = cp.diag(gamma) - W
    constraints = [mat_constraint >> 0]  # ">> 0" denotes PSD in cvxpy
    
    # Objective: Minimize sum of gamma
    objective = cp.Minimize(cp.sum(gamma))
    
    prob = cp.Problem(objective, constraints)
    
    start_time = time.time()
    try:
        prob.solve(solver=cp.SCS, eps=1e-3)
    except cp.error.SolverError:
        return None
        
    return prob.value, time.time() - start_time

def solve_naive_random(W, n):
    """
    Part B.b: "Naive" Random Solution.
    x* = sign(randn(n, 1))
    """
    start_time = time.time()
    
    # Generate random Gaussian vector
    rand_vec = np.random.randn(n)
    # Take sign (handle 0s by defaulting to 1)
    x = np.sign(rand_vec)
    x[x == 0] = 1
    
    # Calculate Objective: x.T * W * x
    val = x.T @ W @ x
    
    return val, time.time() - start_time

def solve_greedy(W, n):
    """
    Part B.c: Greedy Solution.
    Iteratively decides x[k] to be +1 or -1 based on which yields a higher objective
    given the previous decisions.
    """
    start_time = time.time()
    
    x = np.zeros(n)
    
    for k in range(n):
        # Option 1: Set k-th element to 1
        y = x.copy()
        y[k] = 1
        val_y = y.T @ W @ y
        
        # Option 2: Set k-th element to -1
        z = x.copy()
        z[k] = -1
        val_z = z.T @ W @ z
        
        # Greedy Choice
        if val_y >= val_z:
            x = y
        else:
            x = z
            
    final_val = x.T @ W @ x
    return final_val, time.time() - start_time

def main():
    dimensions = [2, 10, 50, 100]
    num_simulations = 100  # As requested in the prompt
    
    print(f"{'n':<4} | {'Runs':<4} | {'Method':<10} | {'Avg Value':<12} | {'Avg Time (s)':<12}")
    print("-" * 60)

    for n in dimensions:
        results = {
            'SDP (A)': {'val': 0.0, 'time': 0.0},
            'SDPdual(B)': {'val': 0.0, 'time': 0.0},
            'Rand (C)': {'val': 0.0, 'time': 0.0},
            'Greedy(D)': {'val': 0.0, 'time': 0.0}
        }
        
        for _ in range(num_simulations):
            W = generate_symmetric_psd_matrix(n)
            
            # 1. Solve SDP
            val_sdp, time_sdp = solve_spectral_relaxation(W, n)
            results['SDP (A)']['val'] += val_sdp
            results['SDP (A)']['time'] += time_sdp
            
            # 2. Solve SDP
            val_sdp, time_sdp = solve_sdp_dual(W, n)
            results['SDPdual(B)']['val'] += val_sdp
            results['SDPdual(B)']['time'] += time_sdp
            
            # 3. Solve Random
            val_rnd, time_rnd = solve_naive_random(W, n)
            results['Rand (C)']['val'] += val_rnd
            results['Rand (C)']['time'] += time_rnd
            
            # 4. Solve Greedy
            val_grd, time_grd = solve_greedy(W, n)
            results['Greedy(D)']['val'] += val_grd
            results['Greedy(D)']['time'] += time_grd
            
        # Print Averaged Results for this dimension
        for method, data in results.items():
            avg_val = data['val'] / num_simulations
            avg_time = data['time'] / num_simulations
            print(f"{n:<4} | {num_simulations:<4} | {method:<10} | {avg_val:<12.2f} | {avg_time:<12.4f}")
        print("-" * 60)

if __name__ == "__main__":
    main()