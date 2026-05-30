import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
import time

N1 = 41
G1 = nx.complete_graph(N1)
print(f"# edges: {G1.number_of_edges()}")
print(f"# nodes: {G1.number_of_nodes()}")

N2 = 10
# FIXED: The tree has N2+2 total nodes. The sequence must be able to randomly 
# pick ANY valid node label (0 through N2+1) to guarantee uniform distribution.
code = [random.randint(0, N2 + 1) for i in range(N2)]
print("Prufer Code:", code)

decoding = nx.from_prufer_sequence(code)
plt.figure()
nx.draw(decoding, with_labels=True, font_weight='bold', node_color='lightblue')
plt.title("Tree from Prüfer Sequence")


def r_regular_1(N=10, r=4):
    G = nx.Graph()
    V = [i for i in range(N)]
    random.shuffle(V)
    
    V1 = V[:N//2]
    V2 = V[N//2:]
    
    for i in range(N//2):
        G.add_edge(V1[(i)%(N//2)], V1[(i+1)%(N//2)])
        G.add_edge(V2[(i)%(N//2)], V2[(i+1)%(N//2)])
        for j in range(r-3+1): 
            G.add_edge(V1[(i)%(N//2)], V2[(i+j)%(N//2)])
            
    return G, (r-2)*(N//2) 

G1_reg, iterations1 = r_regular_1()


def r_regular_2(N=10, r=4):
    total_nodes = N * r
    iterations = 0 
    
    while True:
        iterations += 1
        G = nx.Graph()
        G.add_nodes_from(range(total_nodes))

        nodes = list(G.nodes())
        random.shuffle(nodes)
        groups = [nodes[i * r:(i + 1) * r] for i in range(N)]

        matching_edges = []
        available_nodes = set(nodes)
        attempts = 0

        while len(matching_edges) < total_nodes // 2 and attempts < 1000:
            u, v = random.sample(sorted(available_nodes), 2) 
            matching_edges.append((u, v)) 
            available_nodes.remove(u)
            available_nodes.remove(v)
            attempts += 1

        if len(matching_edges) < total_nodes // 2:
            continue

        G.add_edges_from(matching_edges)

        H = nx.Graph()
        group_map = {}
        for i, group in enumerate(groups):
            for node in group:
                group_map[node] = i
            H.add_node(i)

        invalid = False
        for u, v in matching_edges:
            group_u = group_map[u]
            group_v = group_map[v]

            if group_u == group_v:
                invalid = True
                break
            if H.has_edge(group_u, group_v):
                invalid = True
                break

            H.add_edge(group_u, group_v)

        if invalid:
            continue

        if all(deg == r for _, deg in H.degree()):
            return H, iterations

G2_reg, iterations2 = r_regular_2()


iter_list = []
start = time.time()
N = 10
r = 8
for j in range(4, r):
    iterations_j = []
    for i in range(N):
        _, iterations = r_regular_1(10*i, j)
        iterations_j.append(iterations)
    iter_list.append(iterations_j)
end = time.time()
print(f"Time taken: {end - start:.4f} seconds")

# Matrix for R_regular_2 tracking
N_max = 5
R_max = 8
iter_array = np.zeros((R_max-4, N_max)) 

# Note: Added print statements to track progress, as this loop can take a while!
print("Starting Configuration Model matrix generation...")
for r_val in range(R_max-4, R_max): 
    for n_val in range(1, N_max+1): 
        _, iters = r_regular_2(10*n_val, r_val)
        iter_array[r_val-(R_max-4), n_val-1] = iters
print("Matrix complete:\n", iter_array)


E = [(1,2),(1,3),(3,2),(4,2),(3,4),(5,6),(5,8),(6,7),(6,8),(7,8)]
G_swap = nx.Graph(E)

H_swap = G_swap.copy()
H_swap.remove_edge(2,4)
H_swap.remove_edge(6,8)
H_swap.add_edge(2,6)
H_swap.add_edge(8,4)

same_deg = True
for v in G_swap.nodes():
    if G_swap.degree(v) != H_swap.degree(v):
        same_deg = False
print(f"Degrees perfectly preserved after swap: {same_deg}")


N_forest = 12
K = N_forest // 4
V_forest = [i for i in range(N_forest)]

# FIXED: Slicing to the end of an array requires the index to be `N_forest`, not `N_forest-1`. 
# We also sample strictly from `range(1, N_forest)` to guarantee we never pick 0, 
# preventing an empty slice `[0:0]` that crashes the generator.
partition_indices = [0] + sorted(random.sample(range(1, N_forest), k=K)) + [N_forest]
print("Partition Indices:", partition_indices)

node_sets = [V_forest[partition_indices[j] : partition_indices[j+1]] for j in range(len(partition_indices)-1)]
print("Node Sets:", node_sets)

Trees = []
for V_ in node_sets:
    new_tree = nx.random_unlabeled_tree(len(V_))
    # map unlabeled nodes to our specific subset
    dic = dict(zip(new_tree.nodes(), V_))
    nx.relabel_nodes(new_tree, dic, copy=False)
    Trees.append(new_tree)

Forest = nx.union_all(Trees)

plt.figure()
nx.draw(Forest, with_labels=True, font_weight='bold', node_color='lightgreen')
plt.title("Random Forest")
plt.show()