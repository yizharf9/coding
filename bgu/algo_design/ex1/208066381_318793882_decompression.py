"""
Done by yizhar fahima 208066381
        eyal rothschild 318793882
"""
import sys
import re
from collections import deque, Counter
from typing import List, Dict, Tuple, Union

# ==========================================
# Implementation Area
# ==========================================

# Use a delimiter that is unlikely to appear in the text (Null character).
# The compression script must also use this delimiter to join the lists.
DELIMITER = '\0'  
OUTPUT_FILENAME = "./208066381_318793882_decompressed.txt"

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

def get_tokens(text: str) -> List[str]:
    pattern = r"[A-Za-z]+(?:'[A-Za-z]+)*|[^A-Za-z]"
    return re.findall(pattern, text)

def build_from_traversals(postorder: List, inorder: List):
    if not postorder:
        return None
        
    root_val = postorder.pop()
    
    # Handle the case where the list might contain empty strings due to splitting issues
    # or if recursion reaches a base case incorrectly.
    if len(inorder) == 0:
        return Node(root_val, freq=0)

    try:
        root_idx = inorder.index(root_val)
    except ValueError:
        # If the root value is not in the current inorder slice, 
        # it indicates a structural mismatch or duplicate values in internal nodes.
        # Returning a leaf as a fallback.
        return Node(root_val, freq=0)
    
    # Note: The order of recursion must be Right then Left because 
    # we are popping from the end of a Postorder list (Left, Right, Root).
    right_subtree = inorder[root_idx+1:]
    # Only recurse if there are elements to process
    right_subtree_root = build_from_traversals(postorder, right_subtree) if right_subtree else None
    
    left_subtree = inorder[:root_idx]
    left_subtree_root = build_from_traversals(postorder, left_subtree) if left_subtree else None
    
    root = Node(root_val, freq=0)
    root.left = left_subtree_root
    root.right = right_subtree_root
    
    return root 

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

def generate_codes(root: Node, current_code: str = "", mapping: Dict[str, str] = None) -> Dict[str, str]:
    if mapping is None:
        mapping = {}
    
    if root is None:
        return mapping

    if root.is_leaf():
        mapping[root.value] = current_code
        return mapping
    
    if root.left:
        generate_codes(root.left, current_code + "0", mapping)
    if root.right:
        generate_codes(root.right, current_code + "1", mapping)
        
    return mapping

def decode_from_bit_string(bit_string, code_map):
    decoded_str_list = []
    encoding_list = []
    idx = 0
    total_length = len(bit_string)
    
    # Optimization: Convert code_map to a dict for O(1) lookups if needed, 
    # or keep as list of tuples if prefix matching is required.
    # Since this is a prefix code, we can check prefixes.
    
    while idx < total_length:
        found = False
        # Checking every code in the map against the current substring
        for key, encoding in code_map:
            if bit_string.startswith(encoding, idx):
                decoded_str_list.append(key)
                encoding_list.append(encoding)
                idx += len(encoding)
                found = True
                break
        
        if not found:
            # Prevent infinite loop if no code matches
            print(f"Error: No matching code found at index {idx}")
            break
            
    return decoded_str_list, encoding_list

# ==========================================
# Main Execution 
# ==========================================

def main():
    if len(sys.argv) != 2:
        print("Usage: python 208066381_318793882_decompression.py <file.txt>")
        sys.exit(1)
    
    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    output_filename = OUTPUT_FILENAME
    
    if not lines:
        with open(output_filename, "w", encoding="utf-8") as f:
            pass
        sys.exit(0)
    
    # ==========================================  
    # Parsing
    try:
        # Strip newlines from the lines themselves, then split by the null delimiter
        encoded_text = lines[0].rstrip('\n')
        postorder_str = lines[1].rstrip('\n')
        inorder_str = lines[2].rstrip('\n')
        
        postorder = postorder_str.split(DELIMITER)
        inorder = inorder_str.split(DELIMITER)
    except IndexError:
        print("Error: Input file format incorrect. Expected at least 3 lines.")
        sys.exit(1)
    
    # Sanity check to ensure empty strings from splitting are handled if necessary
    postorder = [x for x in postorder if x != ""]
    inorder = [x for x in inorder if x != ""]

    rec_tree_root = build_from_traversals(postorder, inorder)
    
    # If tree reconstruction failed
    if rec_tree_root is None:
        print("Error: Failed to reconstruct Huffman tree.")
        sys.exit(1)

    code_map = generate_codes(rec_tree_root)
    code_map = sorted(code_map.items(), key=lambda x: int(x[1]) if x[1].isdigit() else 0, reverse=True)
    
    print(f"code_map   : {code_map}")
    
    # 'list' is a reserved keyword, renamed to 'bit_chars'
    bit_chars = [char for char in encoded_text]
    bit_string = "".join(bit_chars)
    print(f"bit_string : {bit_string}")
    
    decoded_str_list, encoding_list = decode_from_bit_string(bit_string, code_map)
    
    print(f"decoded_str_list: {decoded_str_list}")
    print(f"encoding_list:    {encoding_list}")

    # ==========================================  
    decoded_text = "".join(decoded_str_list)
    # ==========================================
    
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(decoded_text) # Removed extra "\n" to preserve exact original content
    except IOError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("\n" + "-"*8 + f"starting decompression of {OUTPUT_FILENAME}" + "-"*8 + '\n')
    main()