"""
Done by yizhar fahima 208066381
        eyal rothschild 318793882
"""
import sys

# ==========================================
# Implementation Area
# ==========================================
import re
from collections import deque, Counter
from typing import List, Dict, Tuple, Union

OUTPUT_FILENAME = "./208066381_318793882_compressed.txt"

class Node:
    def __init__(self, value: Union[str, int], freq: int, left=None, right=None):
        self.value = value
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None

    def __repr__(self):
        return f"Node({self.value}, {self.freq})"

def print_huffman_tree(node, prefix="", is_last=True):
    if node is None:
        return

    connector = "└── " if is_last else "├── "

    if node.left is None and node.right is None:
        content = f"LEAF {repr(node.value)} (freq={node.freq})"
    else:
        content = f"INTERNAL (freq={node.freq})"

    print(prefix + connector + content)

    child_prefix = prefix + ("    " if is_last else "│   ")
    
    children = [child for child in [node.left, node.right] if child]
    for i, child in enumerate(children):
        is_last_child = (i == len(children) - 1)
        print_huffman_tree(child, child_prefix, is_last_child)

def get_tokens(text: str) -> List[str]:
    pattern = r"[A-Za-z]+(?:'[A-Za-z]+)*|[^A-Za-z]"
    return re.findall(pattern, text)

def build_huffman_tree(tokens: List[str]) -> Node:
    if not tokens:
        return None

    counts = Counter(tokens)
    sorted_items = sorted(counts.items(), key=lambda x: (x[1], x[0]))

    q1 = deque([Node(value=item, freq=freq) for item, freq in sorted_items])
    q2 = deque()

    def get_min_node() -> Node:
        if not q1:
            return q2.popleft()
        if not q2:
            return q1.popleft()
        
        if q1[0].freq <= q2[0].freq:
            return q1.popleft()
        else:
            return q2.popleft()

    while len(q1) + len(q2) > 1:
        left = get_min_node()
        right = get_min_node()

        merged_freq = left.freq + right.freq
        parent = Node(value=1, freq=merged_freq, left=left, right=right)
        
        q2.append(parent)

    return q1[0] if q1 else q2[0]

def get_traversals(root: Node) -> Tuple[List[str], List[str]]:
    post_order_list = []
    in_order_list = []

    def _postorder(node):
        if not node: return
        _postorder(node.left)
        _postorder(node.right)
        post_order_list.append(str(node.value))

    def _inorder(node):
        if not node: return
        _inorder(node.left)
        in_order_list.append(str(node.value))
        _inorder(node.right)

    _postorder(root)
    _inorder(root)
    return post_order_list, in_order_list

def generate_codes(root: Node, current_code: str = "", mapping: Dict[str, str] = None) -> Dict[str, str]:
    if mapping is None:
        mapping = {}
    
    if root.is_leaf():
        mapping[root.value] = current_code
        return mapping
    
    if root.left:
        generate_codes(root.left, current_code + "0", mapping)
    if root.right:
        generate_codes(root.right, current_code + "1", mapping)
        
    return mapping

def pack_bits_to_chars(binary_string: str) -> Tuple[str, int]:
    length = len(binary_string)
    padding = (8 - (length % 8)) % 8
    
    padded_binary = binary_string + ('0' * padding)
    
    chars = []
    for i in range(0, len(padded_binary), 8):
        byte_segment = padded_binary[i:i+8]
        char_code = int(byte_segment, 2)
        chars.append(chr(char_code))
        
    return "".join(chars), padding

# ==========================================
# Main Execution 
# ==========================================

def main():
    if len(sys.argv) != 2:
        print("Usage: python 208066381_318793882_compression.py <file.txt>")   #Change ID's
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    output_filename = "208066381_318793882_compressed.txt"    #Change ID's
    
    if not text:
        with open(output_filename, "w", encoding="utf-8") as f:
            pass
        sys.exit(0)
    
    # ==========================================  
    # previously written code 
    tokens = get_tokens(text)
    if not tokens:
        sys.exit(0)

    root = build_huffman_tree(tokens)
    post_order, in_order = get_traversals(root)

    post_order_str = ",".join(repr(t) if t != '1' else '1' for t in post_order)
    in_order_str = ",".join(repr(t) if t != '1' else '1' for t in in_order)

    code_map = generate_codes(root)
    print(code_map)
    encoded_bits = "".join([code_map[t] for t in tokens])

    compressed_content, padding = pack_bits_to_chars(encoded_bits)
# ==========================================  
    encoded_text = compressed_content
    postorder_list = post_order_str
    inorder_list = in_order_str
# ==========================================
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(encoded_text + "\n")
            f.write(",".join(postorder_list) + "\n")
            f.write(",".join(inorder_list) + "\n")
    except IOError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()