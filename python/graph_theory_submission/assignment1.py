import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt

# subsection A
G = nx.random_regular_graph(4,10)
nx.draw(G, with_labels=True, font_weight='bold')

# subsections (B + E + F) 
"""
- dotan's algorithm is implemented although it isn't uniform and not required...
- the graphs take as arguments the number of nodes and the common degree which satisfies subsection F and G in the question
- further explanations required are in the hand-written theoretical part of the submission
"""
def r_regular_1(N = 10, r = 4):
  # initializing an empty graph
  G = nx.Graph()
  # initializing a vertex set of size N
  V = [i for i in range(N)]
  # randomly permutating the vertices
  random.shuffle(V)
  # dividing all the vertices to two groups V1,V2
  V1 = V[:N//2]
  V2 = V[N//2:]
  # iterating over all vertices
  for i in range(N//2):
    # connecting every 2 consecutive vertices in each of the subsets V1,V2 to form a cycle graph (K2)
    G.add_edge(V1[(i)%(N//2)],V1[(i+1)%(N//2)])
    G.add_edge(V2[(i)%(N//2)],V2[(i+1)%(N//2)])
    # matching consecutively a vertex from V1 to a vertex in V2
    for j in range(r-3+1): # practically preforming r-3 iterations...
      # simulating a cyclic permutation and repeating the previous step
      G.add_edge(V1[(i)%(N//2)],V2[(i+j)%(N//2)])
  return G,(r-2)*(N//2) # number of iterations is dictated by N and r in a constant formula

def r_regular_2(N = 10, r = 4):
    total_nodes = N * r
    iterations = 0 # keeping track of number of iterations for later subsections
    while True:
        iterations +=1
        # init. an empty graph containing all nodes {1...N*r}
        G = nx.Graph()
        G.add_nodes_from(range(total_nodes))

        # random partition to groups of size r
        nodes = list(G.nodes())
        random.shuffle(nodes)
        groups = [nodes[i * r:(i + 1) * r] for i in range(N)]

        # init. variables for random matching between all the nodes
        matching_edges = []
        available_nodes = set(nodes)
        attempts = 0

        while len(matching_edges) < total_nodes // 2 and attempts < 1000:
            u, v = random.sample(sorted(available_nodes), 2) # sampling randomly to assure random matching
            matching_edges.append((u, v)) # add the edge to the current matching of the iteration
            available_nodes.remove(u)
            available_nodes.remove(v)
            attempts += 1

        # if the number of edges is less than half the nodes,
        # that means that there is at least one unmatched node
        # therefore, not enough edges to justify the matching and we continue to the next iteration
        if len(matching_edges) < total_nodes // 2:
            continue

        # adding all new matchings to the graph
        G.add_edges_from(matching_edges)

        # we take each group and combine all nodes inside it to a single node
        # thats connected the all the nodes that the nodes in the group were connected to
        H = nx.Graph()
        group_map = {}
        # we map each node to it's group via hashmap
        for i, group in enumerate(groups):
            for node in group:
                group_map[node] = i
            H.add_node(i)

        # we assure that every matching is valid so we iterate over the matchings and verify the following:
        invalid = False
        for u, v in matching_edges:
            group_u = group_map[u]
            group_v = group_map[v]

            # if a matching contains two nodes from the same group,
            # the matching is invalid and we need to enter another iteration
            # until we get matchings only between different groups
            if group_u == group_v:
                invalid = True
                break


            # if a matching yields 2 edges between 2 groups then
            # the matching is invalid and we need to enter another iteration
            # until we get unique matchings between groups
            if H.has_edge(group_u, group_v):
                invalid = True
                break


            H.add_edge(group_u, group_v)

        if invalid:
            continue

        # reassuring that the graph is r-reglular as requested
        if all(deg == r for _, deg in H.degree()):
            return H,iterations

# drawing the output graph of irit's algorithm
G = r_regular_2()
nx.draw(G, with_labels=True, font_weight='bold')

# subsections (H + I)
"""
- we run irit's algorithm for all required parameters (N=20,40,...,100 ; r=4,5,...7)
- r = 8 took over 30min to finish all iterations so we didn't add it in the pictures
- the number of iterations of every run is stored in the "iter_array" matrix for convenience and plotted accordingly
"""
# the code for storing all iteration numbers 
N = 5
R = 8
iter_array = np.zeros((R-4,N)) # r=4,5,6 ; N=20,40,60,80,100
for r in range(R-4,R): # iterating over all degrees - R
  for n in range(1,N+1): # SUBSECTION iterating over all total number of nodes - N
    G2,iterations = r_regular_2(10*n,r)
    iter_array[r-(R-4),n-1] = iterations
print(iter_array)

# the code for plotting the iterations against the number of total nodes N for every degree r (total of 4 plots in practice)

for i,iters in enumerate(iter_array) :
  X = [i for i in range(20,101,20)]
  Y = iters
  plt.figure()
  plt.plot(X,Y)
  plt.title(f"r = {i + 4}")

# the code for plotting the iterations against the degree r for every number of total nodes N (total of 5 plots in practice)

for i,iters in enumerate(iter_array.T) :
  X = [i for i in range(4,8)]
  Y = iters
  plt.figure()
  plt.plot(X,Y)
  plt.title(f"N = {(i+1)*20}")