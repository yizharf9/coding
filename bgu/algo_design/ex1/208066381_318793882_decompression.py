"""
Done by yizhar fahima 208066381
        eyal rothschild 318793882
"""
import sys
from collections import deque, Counter
from typing import List, Dict, Tuple, Union

# ==========================================
# Constants
# ==========================================
DELIMITER = '\0'  # Separates items WITHIN a list (postorder/inorder)
SECTION_SEP = "<<<<SECTION>>>>"  # Separates the 3 main parts of the file
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

def build_from_traversals(postorder: List, inorder: List):
    if not postorder:
        return None
        
    root_val = postorder.pop()
    
    if len(inorder) == 0:
        return Node(root_val, freq=0)

    try:
        root_idx = inorder.index(root_val)
    except ValueError:
        return Node(root_val, freq=0)
    
    # Recursion must correspond to Postorder pop (Right then Left)
    right_subtree = inorder[root_idx+1:]
    right_subtree_root = build_from_traversals(postorder, right_subtree) if right_subtree else None
    
    left_subtree = inorder[:root_idx]
    left_subtree_root = build_from_traversals(postorder, left_subtree) if left_subtree else None
    
    root = Node(root_val, freq=0)
    root.left = left_subtree_root
    root.right = right_subtree_root
    
    return root 

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
    
    # O(N*K) naive decoding (Performance Optimization deferred)
    while idx < total_length:
        found = False
        for key, encoding in code_map:
            if bit_string.startswith(encoding, idx):
                decoded_str_list.append(key)
                encoding_list.append(encoding)
                idx += len(encoding)
                found = True
                break
        
        if not found:
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
    print("\n"+"-"*8+f"starting compression of {input_file}"+"-"*8+'\n')
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            file_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    if not file_content:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            pass
        sys.exit(0)
    
    # ==========================================  
    # Parsing with robust separators
    # ==========================================
    try:
        parts = file_content.split(SECTION_SEP)
        
        if len(parts) < 3:
            raise IndexError
            
        # FIX APPLIED HERE:
        # Changed .strip() to .strip('\r\n')
        # This removes only newlines, preserving actual Space tokens.
        encoded_text = parts[0].strip('\r\n')
        postorder_str = parts[1].strip('\r\n')
        inorder_str = parts[2].strip('\r\n')
        
        postorder = postorder_str.split(DELIMITER)
        inorder = inorder_str.split(DELIMITER)
        
    except IndexError:
        print("Error: Input file format incorrect. Expected 3 sections.")
        sys.exit(1)
    
    # Filter out empty strings if the split created any artifacts (optional safety)
    postorder = [x for x in postorder if x != ""]
    inorder = [x for x in inorder if x != ""]

    rec_tree_root = build_from_traversals(postorder, inorder)
    
    if rec_tree_root is None:
        print("Error: Failed to reconstruct Huffman tree.")
        sys.exit(1)

    code_map = generate_codes(rec_tree_root)
    # Sorting by length (descending) is often safer for prefix checks in naive decoding
    code_map = sorted(code_map.items(), key=lambda x: int(x[1]) if x[1].isdigit() else 0, reverse=True)
    
    bit_chars = [char for char in encoded_text]
    bit_string = "".join(bit_chars)
    
    decoded_str_list, encoding_list = decode_from_bit_string(bit_string, code_map)
    print(f"decoded_str_list : {decoded_str_list}")
    print(f"encoding_list : {encoding_list}")
    
    decoded_text = "".join(decoded_str_list)
    
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write(decoded_text)
    except IOError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()