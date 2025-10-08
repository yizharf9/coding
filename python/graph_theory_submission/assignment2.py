import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
from math import comb


N = 20 # num of nodes
k = 15 # dictates prob.

def create_q_random_graph(N = 20,k = 15,Base_G = None):
    """
    we build a random adjacency matrix and form a graph from it.
    we take advantage of the uniform dist. of the np.random function.
    if the entry i,j or j,i is 1 after comparing to q, using the nx.Graph(...) to create the graph adds the edge {i,j}.
    that is because we used nx.Graph(...) and not nx.DiGraph(...).
    this is according to the definition of the prob. q given in the assignment
    """
    q = k/100 # prob
    adj_matrix = np.random.rand(N,N) < q # matrix entries that are uniformly dist. over [0,1] have a prob. q to be lower than q
    if Base_G is not None : 
        M = nx.convert_matrix.to_numpy_array(Base_G)
        M_indicies = M > 0
        adj_matrix[M_indicies] = 1
        # print(adj_matrix)
    adj_matrix = np.array(adj_matrix *(np.ones((N,N)) - np.eye(N)),dtype=int) # remove diag. of adjacency matrix to prevent self loops
    G = nx.Graph(adj_matrix) # create a new graph based on the adj. matrix
    return G

# Question 1 :

def q_random_graph_q_sweep(N=20):
    precenteges_of_connected = []
    for k in range(5,100,5) :
        num_of_fully_connected = 0
        for i in range(10):
            G = create_q_random_graph(N,k)
        if nx.is_connected(G) : # this is an nx implementation of checking if the graph is connected using BFS
            num_of_fully_connected += 1
        precenteges_of_connected.append(num_of_fully_connected*10)
    return precenteges_of_connected

N = 20
precenteges_1 = q_random_graph_q_sweep(N)
plt.figure()
plt.plot([i/100 for i in range(5,100,5)],precenteges_1)
plt.title("Q1 : precentege of connected graphs")
plt.xlabel("q")
plt.ylabel("C(q)[%]")

# Question 2 :

def q_random_graph_N_sweep(k = 50,s = 10):
    precenteges_of_connected = []
    for N in range(5,100,5) :
        total_num_of_triangles = 0
        for i in range(s):
            G = create_q_random_graph(N,k)
        total_num_of_triangles += sum(nx.triangles(G).values())//3  # this is an nx implementation of counting the amount of triangles in G
                                                                    # it counts every triangle once from each node in the triangle so we divide by 3 ...
        precenteges_of_connected.append(total_num_of_triangles/s)
    return precenteges_of_connected

precenteges_2 = q_random_graph_N_sweep()
plt.figure()
plt.title("Q2 : number of triangles in the graph")
plt.plot([i/100 for i in range(5,100,5)],precenteges_2)
plt.xlabel("q")
plt.ylabel("t3(q)[%]")

# Question 3 :

def q_random_graph_q_sweep(N = 20 ,k = 50,s = 10,Base_G = nx.Graph()):
    if nx.is_empty(Base_G):
        Base_G.add_nodes_from([i for i in range(N)])

    average_eccentricities = []
    for k in range(5,100,5) :
        sum_of_avg_eccentricities = 0
        for i in range(s):
            G = create_q_random_graph(N,k,Base_G)
        try :
            eq = sum(nx.eccentricity(G).values())/G.number_of_nodes()
        except : 
            eq = N+1
        sum_of_avg_eccentricities += eq
        average_eccentricities.append(sum_of_avg_eccentricities/s)

    return average_eccentricities

N = 20
Base_Path = nx.path_graph(N)
avg_ecc_path = q_random_graph_q_sweep(N = N,Base_G=Base_Path)
Base_cycle = nx.cycle_graph(N)
avg_ecc_cycle = q_random_graph_q_sweep(N = N,Base_G=Base_cycle)
plt.figure()
plt.title("Q3 : average ecc. using Path/Cycle as Base graph")

plt.plot([i/100 for i in range(5,100,5)],avg_ecc_path,label = "path")
plt.xlabel("q")
plt.ylabel("e_q(G1)")
plt.plot([i/100 for i in range(5,100,5)],avg_ecc_cycle,"--",label = "cycle")
plt.xlabel("q")
plt.ylabel("e_q(G2)")
plt.legend(loc="upper left")
plt.show()