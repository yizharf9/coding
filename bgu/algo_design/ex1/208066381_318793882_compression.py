import sys
import re
from collections import Counter, deque

ID1 = "208066381"
ID2 = "318793882"
LIST_DELIMITER = '\0'

class Node:
    def __init__(self, value, freq, left=None, right=None):
        self.value = str(value)
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None

def get_tokens(text):
    pattern = r"[A-Za-z]+(?:'[A-Za-z]+)*|[ ]|[^A-Za-z ]"
    return re.findall(pattern, text)

def build_huffman_tree(tokens):
    if not tokens:
        return None
    
    counts = Counter(tokens)
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
    output_filename = f"{ID1}_{ID2}_compressed.txt"
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    if not text:
        with open(output_filename, 'w', encoding='utf-8') as f:
            pass
        return

    tokens = get_tokens(text)
    root = build_huffman_tree(tokens)
    post_order, in_order = get_traversals(root)
    
    code_map = {}
    get_codes(root, "", code_map)
    encoded_bits_str = "".join(code_map[t] for t in tokens)
    
    extra_padding = 8 - (len(encoded_bits_str) % 8)
    if extra_padding == 8:
        extra_padding = 0
        
    final_bits = encoded_bits_str + ("0" * extra_padding)
    
    packed_chars = []
    packed_chars.append(chr(extra_padding))
    
    for i in range(0, len(final_bits), 8):
        byte_str = final_bits[i:i+8]
        byte_val = int(byte_str, 2)
        packed_chars.append(chr(byte_val))
        
    compressed_content = "".join(packed_chars)

    try:
        with open(output_filename, 'w', encoding='latin-1', newline='\n') as f:
            f.write(compressed_content + "\n")
            f.write(LIST_DELIMITER.join(post_order) + "\n")
            f.write(LIST_DELIMITER.join(in_order))
            
    except IOError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()