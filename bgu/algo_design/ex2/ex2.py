import numpy as np
import matplotlib.pyplot as plt
import sys

import networkx as nx #! remove before submission , will be graded 0!!!

class TarjanSCC() :
    def __init__(self,adj_mat:np.ndarray,T:list[int],G:list[int]):
        self.adj_mat = adj_mat
        N = adj_mat.shape[0]
        
        self.adj_list = []
        for node in range(N):
            node_neighbors = []
            for neighbor in range(N):
                if adj_mat[node,neighbor] == 1:
                    node_neighbors.append(neighbor)
            self.adj_list.append(node_neighbors)
        
        self.real_T = T
        self.G = G
        
        self.IDs = [-1]*N
        self.Low = [0]*N
        
        self.node_stack = [] # all nodes initiated to not discovered in initialization
        self.nodes_in_stack = [False]*N # all nodes not in stack in initialization
        self.timer = 0
        
        self.SCC_count = -1
    
    def time_inc(self):
        self.timer += 1
    
    def DFS(self,at:int,p_flag = True):
        
        self.node_stack.append(at)
        self.nodes_in_stack[at] = True
        
        self.IDs[at] = self.timer
        self.Low[at] = self.timer
        
        self.time_inc()
        N = self.adj_mat.shape[0]
        
        if p_flag : 
            print(f"\ntime:{self.timer}")
            print(f"at : {at}")
            
        for to in self.adj_list[at]:
            if p_flag : 
                print(f"to : {to}",end=" ") 
                print()
            if self.IDs[to] == -1 : 
                self.DFS(to,p_flag)
            if self.nodes_in_stack[to] :
                self.Low[at] = min(self.Low[at],self.Low[to])
        
        
        if self.IDs[at] == self.Low[at] :
            while len(self.node_stack) > 0 :
                node = self.node_stack.pop()
                self.nodes_in_stack[node] = False
                self.Low[node] = self.IDs[at]
                if node == self.IDs[at] :
                    break
        self.SCC_count +=1
    
    def count_SCC(self,P_flag = True):
        N = len(self.adj_list)
        for i in range(N):
            if self.IDs[i] == -1 :
                self.DFS(i,p_flag=P_flag)
        return self.Low


def initiate_sample_data_file(path = "./data.txt",N = 10 ,p = 0.25,test_example = True):
    if not test_example :
        data_mat = np.random.rand(N,N) <= p
        data_mat = np.array(data_mat,dtype=int)
        print(data_mat)
        
        T = np.random.randint(1,N,N)
        G = np.random.randint(1,N,N)
        with open(path,"w") as f :
            lines = []
            for i in range(N) :
                added_line = ""
                for j in range(N):
                    if i != j :
                        added_line += str(data_mat[i,j]) + " "
                    else :
                        added_line += str(T[i]) + "," + str(G[i]) + " "
                lines.append(added_line + "\n")
            f.writelines(lines)
    else : 
        with open(path,"w") as f :
            mat_string = "2,5 1 0 0\n1 4,1 1 0\n0 0 3,2 1\n0 0 0 1,4"
            f.write(mat_string)

def read_data_file(path = "./data.txt",p_flag = True): #? make sure this answers the actual format of the input
    lines = []
    T = []
    G = []
    with open(path,"r") as f :
        if len(f.read()) == 0 : # empty graph
            return np.array([[]]),T,G
        for i,line in enumerate(f.readlines()):
            line = line.strip()
            line = line.split(" ")
            ti,gi = line[i].split(',')
            line[i] = "0"
            if p_flag : 
                print(line)
                print(i,ti,gi)
            
            T.append(int(ti))
            G.append(int(gi))
            lines.append([int(s) for s in line])
            

    data = np.array(lines)
    if p_flag : 
        print(f"data : \n{data}")
        print(f"T : {T}")
        print(f"G : {G}")
    return data,T,G


if __name__ == "__main__":
    # initiate_sample_data_file(test_example=True)
    if len(sys.argv) != 2 :
        print("invalid arg list for execution!")
        exit()
    
    file_path = sys.argv[1]
    print(f"data path = {file_path}")
    
    data,T,G = read_data_file(path=file_path,p_flag=False)
    N = data.shape[0]
    
    tar = TarjanSCC(data,T,G)
    
    
    print(f"\nadj_mat : \n{data}\n")
    print(f"\nadj_list : ")
    for l in tar.adj_list:
        print(l)
    print(f"\nT : {T}")
    print(f"G : {G}")
    print(f"N : {N}\n\n")
    
    lows = tar.count_SCC(P_flag=False)
    print(f"low link values : {lows}")
    
    #! remove before submission , will be graded 0!!!
    G = nx.DiGraph(data)
    nx.draw(G,with_labels=True,pos=nx.circular_layout(G))
    plt.show()
    
    # get_path(data,0,4)
    
    