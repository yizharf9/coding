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
        self.rep = self.members[0]      # Smallest review ID [cite: 42]
        self.duration = 0
        self.internal_order = []
        self.start_time = 0
        self.finish_time = 0
        self.tasks_map = tasks_map      # Reference to global task dict
        
        # Calculate optimal internal order immediately upon creation
        self._calculate_schedule()

    def _calculate_schedule(self):
        """
        Applies Johnson's Rule to minimize board makespan T[B]. [cite: 47, 58]
        """
        # Split tasks into two groups
        # Group U: t < g (sorted by t ascending)
        # Group V: t >= g (sorted by g descending)
        
        group_u = []
        group_v = []

        for tid in self.members:
            task = self.tasks_map[tid]
            if task.t < task.g:
                group_u.append(task)
            else:
                group_v.append(task)

        # Sort groups
        group_u.sort(key=lambda x: x.t)
        group_v.sort(key=lambda x: x.g, reverse=True)

        # Final order
        ordered_tasks = group_u + group_v
        self.internal_order = [t.id for t in ordered_tasks]

        # Calculate Duration T[B]
        # Rules:
        # 1. Review phase runs sequentially on 1 resource.
        # 2. Integration phase runs sequentially on 1 resource.
        # 3. Integration for task i starts after Review i finishes.
        
        current_review_finish = 0
        current_integration_finish = 0

        for task in ordered_tasks:
            # Review phase
            current_review_finish += task.t
            
            # Integration phase
            # Starts at max(end of previous integration, end of current review)
            start_integration = max(current_integration_finish, current_review_finish)
            current_integration_finish = start_integration + task.g

        self.duration = current_integration_finish

    def __lt__(self, other):
        # Comparison for heap (priority queue) based on Board ID (which respects rep)
        return self.id < other.id

# --- Algorithms ---

def parse_input(filename):
    """
    Reads N x N matrix. 
    Diagonal: t,g
    Off-diagonal: 0 or 1
    """
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    N = len(lines)
    adj = {i: [] for i in range(1, N + 1)}
    tasks = {}

    for r, line in enumerate(lines):
        tokens = line.split()
        u = r + 1 # 1-based index
        
        for c, token in enumerate(tokens):
            v = c + 1 # 1-based index
            
            if u == v:
                # Diagonal: duration info "t,g"
                t_str, g_str = token.split(',')
                tasks[u] = Task(u, int(t_str), int(g_str))
            else:
                # Off-diagonal: dependency "0" or "1"
                if token == '1':
                    adj[u].append(v)
    
    return N, tasks, adj

def find_sccs(N, adj):
    """
    [cite_start]Tarjan's Algorithm to find Strongly Connected Components (Boards). [cite: 39]
    """
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
    """
    1. Create Board objects.
    2. [cite_start]Sort Boards by rep(B) to assign IDs 1..C. [cite: 44]
    3. Build the DAG of Boards.
    """
    # Create temp board objects to determine rep and sort
    temp_boards = []
    for comp in sccs:
        # [cite_start]Rep is smallest review ID in the board [cite: 42]
        rep = min(comp)
        temp_boards.append({'rep': rep, 'members': comp})
    
    # Sort by rep to assign IDs
    temp_boards.sort(key=lambda x: x['rep'])
    
    boards = []
    node_to_board_map = {} # Maps original task ID to Board Object
    
    for idx, b_data in enumerate(temp_boards):
        b_id = idx + 1
        new_board = Board(b_id, b_data['members'], tasks)
        boards.append(new_board)
        for member in b_data['members']:
            node_to_board_map[member] = new_board
            
    # Build DAG (Condensation Graph)
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
    """
    1. [cite_start]Topologically sort boards (using Min-Heap for tie-breaking by ID/rep). [cite: 67]
    2. Calculate S[B] and F[B] (Critical Path Method on DAG).
    """
    # Min-heap for processing order (Prioritize smaller Board ID)
    pq = []
    for b in boards:
        if board_in_degree[b.id] == 0:
            heapq.heappush(pq, b)
            
    execution_order = []
    
    # Map board ID to Board object for easy lookup
    id_to_board = {b.id: b for b in boards}
    
    while pq:
        u_board = heapq.heappop(pq)
        execution_order.append(u_board.id)
        
        # Calculate Start Time: Max Finish Time of predecessors
        # Since we are processing in topo order, predecessors are already processed? 
        # Not necessarily all predecessors for calculating max time, 
        # but topo sort guarantees we visit u before v if u->v.
        
        # However, to strictly calculate S[B] correctly for the critical path logic,
        # we usually just propagate finish times.
        
        current_finish = u_board.start_time + u_board.duration
        u_board.finish_time = current_finish
        
        for v_id in board_adj[u_board.id]:
            v_board = id_to_board[v_id]
            # Update successor start time
            if current_finish > v_board.start_time:
                v_board.start_time = current_finish
            
            board_in_degree[v_id] -= 1
            if board_in_degree[v_id] == 0:
                heapq.heappush(pq, v_board)
                
    return execution_order

def get_critical_path(boards, board_adj):
    """
    [cite_start]Reconstructs one critical path of tasks. [cite: 64, 85]
    [cite_start]Tie-breaker: choose predecessor with smaller rep(B). [cite: 68]
    """
    if not boards:
        return []

    id_to_board = {b.id: b for b in boards}
    
    # reverse adjacency to find predecessors easily
    board_rev_adj = {b.id: [] for b in boards}
    for u_id, v_ids in board_adj.items():
        for v_id in v_ids:
            board_rev_adj[v_id].append(u_id)

    # 1. Identify the board that ends last (Critical Sink)
    max_finish = -1
    for b in boards:
        if b.finish_time > max_finish:
            max_finish = b.finish_time
            
    # Collect all boards that finish at max_finish to pick the start of backtracking
    # (Though logic usually implies we pick the specific sink of the critical path)
    candidates = [b for b in boards if b.finish_time == max_finish]
    # Tie-breaker logic isn't explicitly defined for the *start* of the path, 
    # but based on consistency with predecessors, we pick smaller ID.
    candidates.sort(key=lambda x: x.id)
    curr_board = candidates[0]
    
    path_boards = [curr_board]
    
    # 2. Backtrack
    while True:
        preds = board_rev_adj[curr_board.id]
        if not preds:
            break
            
        # Find predecessors that constrained the start time
        # i.e., F[P] == S[curr]
        critical_preds = []
        for p_id in preds:
            pred_board = id_to_board[p_id]
            if pred_board.finish_time == curr_board.start_time:
                critical_preds.append(pred_board)
        
        if not critical_preds:
            break
            
        # [cite_start]Tie breaker: choose predecessor with smaller rep (which is smaller Board ID) [cite: 68]
        critical_preds.sort(key=lambda x: x.id)
        best_pred = critical_preds[0]
        
        path_boards.append(best_pred)
        curr_board = best_pred
        
    # The path is constructed backwards
    path_boards.reverse()
    
    # [cite_start]3. Concatenate internal orders [cite: 88]
    final_task_path = []
    for b in path_boards:
        final_task_path.extend(b.internal_order)
        
    return max_finish, final_task_path

# --- Main Driver ---

def main():
    if len(sys.argv) < 2:
        print("Usage: python ID1_ID2.py input.txt")
        return

    input_file = sys.argv[1]
    
    # [cite_start]Generate output filename based on script name [cite: 72]
    script_name = os.path.basename(sys.argv[0])
    name_part = os.path.splitext(script_name)[0]
    output_file = f"{name_part}_Output.txt"

    # 1. Parse
    N, tasks, adj = parse_input(input_file)

    # 2. SCCs (Boards)
    sccs = find_sccs(N, adj)

    # 3. Build Board DAG & Internal Scheduling (Johnson's)
    boards, node_to_board, board_adj, in_degree = build_board_graph(sccs, tasks, adj)
    
    # 4. Global Scheduling
    exec_order_ids = schedule_boards(boards, board_adj, in_degree)
    
    # 5. Critical Path
    overall_completion, critical_path_tasks = get_critical_path(boards, board_adj)
    
    # [cite_start]6. Output Generation [cite: 75-88]
    with open(output_file, 'w') as f:
        # Line 1: Number of boards
        f.write(f"{len(boards)}\n")
        
        # Line 2: Overall completion time
        f.write(f"{overall_completion}\n")
        
        # Line 3: Board ID for each task 1..N
        # We must output board IDs sorted by task ID 1..N
        board_ids_by_node = []
        for i in range(1, N + 1):
            board_ids_by_node.append(str(node_to_board[i].id))
        f.write(" ".join(board_ids_by_node) + "\n")
        
        # Line 4: Board execution order
        f.write(" ".join(map(str, exec_order_ids)) + "\n")
        
        # Next C lines: Board details
        # Output strictly in the order given on Line 4 (exec_order_ids)
        id_to_board = {b.id: b for b in boards}
        for b_id in exec_order_ids:
            b = id_to_board[b_id]
            # Format: |b| rep(b) S[b] F[b] T[b] v1 v2 ...
            row = [
                len(b.members),
                b.rep,
                b.start_time,
                b.finish_time,
                b.duration
            ]
            row.extend(b.internal_order)
            f.write(" ".join(map(str, row)) + "\n")
            
        # Final Line: Critical path of tasks (length + tasks)
        # Format: L p1 p2 ...
        cp_row = [len(critical_path_tasks)] + critical_path_tasks
        f.write(" ".join(map(str, cp_row)) + "\n")

if __name__ == "__main__":
    main()