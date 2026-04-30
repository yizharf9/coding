import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

# 1. הגדרת זרע (Seed) לפי תעודת זהות (דוגמה)
np.random.seed(123456789)

# נתוני האמת
true_a = np.array([1, 2, 3, 4, 5, 6, 7, 8]) # וקטור עמודה בגודל 8
true_b = 9
n_features = len(true_a)
k_samples = 100

def generate_data(sigma):
    X = np.random.randn(k_samples, n_features)
    noise = np.random.normal(0, sigma, k_samples)
    y = X @ true_a - true_b + noise
    return X, y

def solve_min_max_regression(X, y):
    n = X.shape[1]
    num_vars = n + 1 + 1 

    c = np.zeros(num_vars)
    c[-1] = 1 

    A_block_1 = -X
    A_block_2 = X

    b_col_1 = np.ones((k_samples, 1))
    b_col_2 = -1 * np.ones((k_samples, 1))

    t_col = -1 * np.ones((k_samples, 1))
    
    top_rows = np.hstack([A_block_1, b_col_1, t_col])    # [-x,  1, -1]
    bottom_rows = np.hstack([A_block_2, b_col_2, t_col]) # [ x, -1, -1]
    
    A_ub = np.vstack([top_rows, bottom_rows])
    
    b_ub = np.concatenate([-y, y])

    bounds = [(None, None)] * num_vars
    
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    if res.success:
        return res.fun
    else:
        return np.nan


variances = np.linspace(0.1, 5, 10) 
num_simulations = 20 
average_errors = []

print("Starting Monte-Carlo simulation...")

for var in variances:
    sigma = np.sqrt(var)
    errors_for_var = []
    
    for _ in range(num_simulations):
        X_sim, y_sim = generate_data(sigma)
        p_star = solve_min_max_regression(X_sim, y_sim)
        errors_for_var.append(p_star)
    
    avg_error = np.mean(errors_for_var)
    average_errors.append(avg_error)
    print(f"Variance: {var:.2f}, Avg Min-Max Error: {avg_error:.4f}")


plt.figure(figsize=(10, 6))
plt.plot(variances, average_errors, marker='o', linestyle='-', color='b')
plt.title('Min-Max Error vs Noise Variance ($\sigma^2$)')
plt.xlabel('Variance ($\sigma^2$)')
plt.ylabel('Average Optimal Error ($p^*$)')
plt.grid(True)
plt.show()