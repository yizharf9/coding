import sys
import re
from collections import Counter, deque

# IDs for filename - Replace with actual IDs
ID1 = "208066381"
ID2 = "318793882"

# Must match the delimiter used in the decompression script
DELIMITER = '\0'

class Node:
    def __init__(self, value, freq, left=None, right=None):
        self.value = str(value)
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None

def get_tokens(text):
    # Matches words/contractions, single spaces, or single punctuation
    pattern = r"[A-Za-z]+(?:'[A-Za-z]+)*|[ ]|[^A-Za-z ]"
    return re.findall(pattern, text)

def build_huffman_tree(tokens):
    if not tokens:
        return None
    
    counts = Counter(tokens)
    # Primary sort by freq, secondary sort by value for determinism
    sorted_items = sorted(counts.items(), key=lambda x: (x[1], x[0]))
    
    q_leaves = deque([Node(val, freq) for val, freq in sorted_items])
    q_internal = deque()
    
    def get_min():
        if not q_internal:
            return q_leaves.popleft()
        if not q_leaves:
            return q_internal.popleft()
        if q_leaves[0].freq <= q_internal[0].freq:
            return q_leaves.popleft()
        return q_internal.popleft()
    
    internal_id = 0
    while (len(q_leaves) + len(q_internal)) > 1:
        left = get_min()
        right = get_min()
        parent = Node(internal_id, left.freq + right.freq, left, right)
        q_internal.append(parent)
        internal_id += 1
        
    return q_leaves[0] if q_leaves else q_internal[0]

def get_traversals(root):
    post_order = []
    in_order = []

    # Re-implemented to avoid recursion depth issues on very large trees
    # but using standard recursive helper for readability as per request
    def _post(n):
        if n:
            _post(n.left)
            _post(n.right)
            post_order.append(n.value)
            
    def _in(n):
        if n:
            _in(n.left)
            in_order.append(n.value)
            _in(n.right)

    _post(root)
    _in(root)
    return post_order, in_order

def get_codes(node, current_code, mapping):
    if node.is_leaf():
        mapping[node.value] = current_code
        return
    get_codes(node.left, current_code + "0", mapping)
    get_codes(node.right, current_code + "1", mapping)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <file.txt>")
        return
        
    input_path = sys.argv[1]
    OUTPUT_FILENAME = f"{ID1}_{ID2}_compressed.txt"
    print("\n"+"-"*8+f"starting compression of {input_path}"+"-"*8+'\n')
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            # Note: Keeping your existing slice [:27] as requested, 
            # but usually you want f.read() for the full file.
            text = f.read()
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    if not text:
        # Create empty file if input is empty
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            pass
        return

    tokens = get_tokens(text)
    print(f"tokens       : {tokens}")
    root = build_huffman_tree(tokens)
    
    post_order, in_order = get_traversals(root)
    
    code_map = {}
    get_codes(root, "", code_map)
    
    encoded_bits = "".join(code_map[t] for t in tokens)
    print(f"encoded_bits : {encoded_bits}")
    
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(encoded_bits + "\n")
            # CHANGED: Using DELIMITER ('\0') instead of ','
            f.write(DELIMITER.join(post_order) + "\n")
            f.write(DELIMITER.join(in_order) + "\n")
    except IOError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()