import numpy as np
import matplotlib.pyplot as plt
import sys

import networkx as nx #! remove before submission , will be graded 0!!!

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

def get_path(adj_mat:np.ndarray,source:int,target:int,path = [])->list[int]:
    if source == target :
        path.append(target)
        return
    _neighbors = adj_mat[source,:]
    for i,neighbor in enumerate(_neighbors):
        if neighbor == 1 :
            print(i)
            path.append(i)
            adj_mat[source,i] = 0 
            get_path(adj_mat,i,target,path)
    return 

if __name__ == "__main__":
    initiate_sample_data_file(test_example=True)
    if len(sys.argv) != 2 :
        print("invalid arg list for execution!")
        exit()
    
    file_path = sys.argv[1]
    print(f"data path = {file_path}")
    
    data,T,G = read_data_file(path=file_path,p_flag=False)
    N = data.shape[0]
    
    print(f"\ndata : \n{data}\n")
    print(f"T : {T}")
    print(f"G : {G}")
    print(f"N : {N}\n\n")
    
    
    # G = nx.DiGraph(data)
    # nx.draw(G,with_labels=True,pos=nx.circular_layout(G))
    # plt.show()
    
    # get_path(data,0,4)
    
    