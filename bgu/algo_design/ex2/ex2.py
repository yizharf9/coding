import numpy as np
import sys


def initiate_sample_data_file(path = "./data.txt",N = 10):
    data_mat = np.random.rand(N,N) <= 0.5
    data_mat = np.array(data_mat,dtype=int)
    print(data_mat)
    
    with open(path,"w") as f :
        lines = []
        for i in range(N) :
            added_line = ""
            for j in range(N):
                if i != j :
                    added_line += str(data_mat[i,j]) + " "
                else :
                    added_line += str(0) + " "
            lines.append(added_line + "\n")
        f.writelines(lines)

def read_data_file(path = "./data.txt",p_flag = True):
    lines = []
    with open(path,"r") as f :
        for line in f.readlines():
            line = line[:-2]
            line = line.split(" ")
            lines.append([int(s) for s in line])
            if p_flag : print(line)
    data = np.array(lines)
    if p_flag : print(data)
    return data

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
    # initiate_sample_data_file()
    if len(sys.argv) != 2 :
        print("invalid arg list for execution!")
        exit()
    
    file_path = sys.argv[1]
    print(f"data path = {file_path}")
    
    data = read_data_file(path=file_path,p_flag=False)
    print(data)
    
    get_path(data,0,4)
    
    