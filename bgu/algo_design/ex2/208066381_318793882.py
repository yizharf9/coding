import numpy as np
import matplotlib.pyplot as plt
import sys

import networkx as nx #! remove before submission , will be graded 0!!!


def initiate_sample_data_file(path = "./input.txt",N = 10 ,p = 0.25,test_example = True,p_flag=False,init_mat=None):
    if init_mat is not None :
        N = len(init_mat)
        T = [0]*N
        G = [0]*N
        for i in range(N):
            T[i] , G[i] = init_mat[i][i]
            init_mat[i][i] = 0
        
        with open(path,"w") as f :
            lines = []
            for i in range(N) :
                added_line = ""
                for j in range(N):
                    if i != j :
                        added_line += str(init_mat[i][j]) + " "
                    else :
                        added_line += str(T[i]) + "," + str(G[i]) + " "
                lines.append(added_line + "\n")
            f.writelines(lines)
    elif not test_example :
        data_mat = np.random.rand(N,N) <= p
        data_mat = np.array(data_mat,dtype=int)
        if p_flag : print(data_mat)
        
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

import sys
import os
import heapq

# --- Data Structures ---

class Task:
    def __init__(self, task_id, t, g):
        self.id = task_id
        self.t = t  # Review time
        self.g = g  # Integration time

class Board:
    def __init__(self, board_id, members, tasks_map):
        self.id = board_id
        self.members = sorted(members)  # List of task IDs in this board
        self.rep = self.members[0]      # Smallest review ID
        self.duration = 0
        self.internal_order = []
        self.start_time = 0
        self.finish_time = 0
        self.tasks_map = tasks_map      # Reference to global task dict
        
        self._calculate_schedule()

    def _calculate_schedule(self):
        """
        Applies Johnson's Rule to minimize board makespan T[B].
        """
        group_u = []
        group_v = []

        for tid in self.members:
            task = self.tasks_map[tid]
            if task.t < task.g:
                group_u.append(task)
            else:
                group_v.append(task)

        group_u.sort(key=lambda x: x.t)
        group_v.sort(key=lambda x: x.g, reverse=True)

        ordered_tasks = group_u + group_v
        self.internal_order = [t.id for t in ordered_tasks]

        current_review_finish = 0
        current_integration_finish = 0

        for task in ordered_tasks:
            current_review_finish += task.t
            start_integration = max(current_integration_finish, current_review_finish)
            current_integration_finish = start_integration + task.g

        self.duration = current_integration_finish

    def __lt__(self, other):
        return self.id < other.id

# --- Algorithms ---

def parse_input(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    N = len(lines)
    adj = {i: [] for i in range(1, N + 1)}
    tasks = {}

    for r, line in enumerate(lines):
        tokens = line.split()
        u = r + 1 
        
        for c, token in enumerate(tokens):
            v = c + 1 
            
            if u == v:
                t_str, g_str = token.split(',')
                tasks[u] = Task(u, int(t_str), int(g_str))
            else:
                if token == '1':
                    adj[u].append(v)
    
    return N, tasks, adj

def find_sccs(N, adj):
    visited = set()
    stack = []
    on_stack = set()
    ids = {}
    low = {}
    id_counter = 0
    sccs = []

    def dfs(at):
        nonlocal id_counter
        stack.append(at)
        on_stack.add(at)
        visited.add(at)
        ids[at] = low[at] = id_counter
        id_counter += 1

        for to in adj[at]:
            if to not in visited:
                dfs(to)
                low[at] = min(low[at], low[to])
            elif to in on_stack:
                low[at] = min(low[at], ids[to])

        if ids[at] == low[at]:
            component = []
            while stack:
                node = stack.pop()
                on_stack.remove(node)
                component.append(node)
                if node == at:
                    break
            sccs.append(component)

    for i in range(1, N + 1):
        if i not in visited:
            dfs(i)

    return sccs

def build_board_graph(sccs, tasks, original_adj):
    temp_boards = []
    for comp in sccs:
        rep = min(comp)
        temp_boards.append({'rep': rep, 'members': comp})
    
    temp_boards.sort(key=lambda x: x['rep'])
    
    boards = []
    node_to_board_map = {} 
    
    for idx, b_data in enumerate(temp_boards):
        b_id = idx + 1
        new_board = Board(b_id, b_data['members'], tasks)
        boards.append(new_board)
        for member in b_data['members']:
            node_to_board_map[member] = new_board
            
    board_adj = {b.id: set() for b in boards}
    board_in_degree = {b.id: 0 for b in boards}
    
    for u in original_adj:
        u_board = node_to_board_map[u]
        for v in original_adj[u]:
            v_board = node_to_board_map[v]
            
            if u_board.id != v_board.id:
                if v_board.id not in board_adj[u_board.id]:
                    board_adj[u_board.id].add(v_board.id)
                    board_in_degree[v_board.id] += 1
                    
    return boards, node_to_board_map, board_adj, board_in_degree

def schedule_boards(boards, board_adj, board_in_degree):
    pq = []
    for b in boards:
        if board_in_degree[b.id] == 0:
            heapq.heappush(pq, b)
            
    execution_order = []
    id_to_board = {b.id: b for b in boards}
    
    while pq:
        u_board = heapq.heappop(pq)
        execution_order.append(u_board.id)
        
        current_finish = u_board.start_time + u_board.duration
        u_board.finish_time = current_finish
        
        for v_id in board_adj[u_board.id]:
            v_board = id_to_board[v_id]
            if current_finish > v_board.start_time:
                v_board.start_time = current_finish
            
            board_in_degree[v_id] -= 1
            if board_in_degree[v_id] == 0:
                heapq.heappush(pq, v_board)
                
    return execution_order

def get_critical_path(boards, board_adj):
    if not boards:
        return 0, []

    id_to_board = {b.id: b for b in boards}
    board_rev_adj = {b.id: [] for b in boards}
    for u_id, v_ids in board_adj.items():
        for v_id in v_ids:
            board_rev_adj[v_id].append(u_id)

    max_finish = -1
    for b in boards:
        if b.finish_time > max_finish:
            max_finish = b.finish_time
            
    candidates = [b for b in boards if b.finish_time == max_finish]
    candidates.sort(key=lambda x: x.id)
    curr_board = candidates[0]
    
    path_boards = [curr_board]
    
    while True:
        preds = board_rev_adj[curr_board.id]
        if not preds:
            break
            
        critical_preds = []
        for p_id in preds:
            pred_board = id_to_board[p_id]
            if pred_board.finish_time == curr_board.start_time:
                critical_preds.append(pred_board)
        
        if not critical_preds:
            break
            
        critical_preds.sort(key=lambda x: x.id)
        best_pred = critical_preds[0]
        
        path_boards.append(best_pred)
        curr_board = best_pred
        
    path_boards.reverse()
    
    final_task_path = []
    for b in path_boards:
        final_task_path.extend(b.internal_order)
        
    return max_finish, final_task_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python ID1_ID2.py input.txt")
        return

    input_file = sys.argv[1]
    script_name = os.path.basename(sys.argv[0])
    name_part = os.path.splitext(script_name)[0]
    output_file = f"{name_part}_Output.txt"

    N, tasks, adj = parse_input(input_file)
    sccs = find_sccs(N, adj)
    boards, node_to_board, board_adj, in_degree = build_board_graph(sccs, tasks, adj)
    exec_order_ids = schedule_boards(boards, board_adj, in_degree)
    overall_completion, critical_path_tasks = get_critical_path(boards, board_adj)
    
    with open(output_file, 'w') as f:
        f.write(f"{len(boards)}\n")
        f.write(f"{overall_completion}\n")
        
        board_ids_by_node = []
        for i in range(1, N + 1):
            board_ids_by_node.append(str(node_to_board[i].id))
        f.write(" ".join(board_ids_by_node) + "\n")
        
        f.write(" ".join(map(str, exec_order_ids)) + "\n")
        
        id_to_board = {b.id: b for b in boards}
        for b_id in exec_order_ids:
            b = id_to_board[b_id]
            row = [
                len(b.members),
                b.rep,
                b.start_time,
                b.finish_time,
                b.duration
            ]
            row.extend(b.internal_order)
            f.write(" ".join(map(str, row)) + "\n")
            
        cp_row = [len(critical_path_tasks)] + critical_path_tasks
        f.write(" ".join(map(str, cp_row)) + "\n")

if __name__ == "__main__":
    
    mat = [
        [0,0,0,0,0],
        [1,0,0,1,0],
        [0,0,0,1,0],
        [1,0,0,0,1],
        [0,0,1,0,0],
    ]
    T = [5,7,1,9,7]
    G = [3,7,1,5,6]
    
    for i in range(len(mat)) :
        mat[i][i] = (T[i],G[i])
    
    
    # initiate_sample_data_file(path = "./input.txt", N = 20 , p = 0.09 , test_example=True,init_mat=mat)
    
    main()