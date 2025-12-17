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

def get_tokens(text: str) -> List[str]:
    pattern = r"[A-Za-z]+(?:'[A-Za-z]+)*|[^A-Za-z]"
    return re.findall(pattern, text)

def build_from_traversals(postorder:List,inorder:List):
        root = postorder.pop()
        # print(f"root = {root} ,inorder = {inorder}\n")
        if len(inorder) == 1 :
            return Node(root,freq=0)
        root_idx = inorder.index(root)
        
        right_subtree = inorder[root_idx+1:]
        right_subtree_root = build_from_traversals(postorder,right_subtree)
        
        
        left_subtree = inorder[:root_idx]
        left_subtree_root = build_from_traversals(postorder,left_subtree)
        
        root = Node(root,freq=0)
        root.left = left_subtree_root
        root.right = right_subtree_root
        # print_huffman_tree(root)
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
    
    if root.is_leaf():
        mapping[root.value] = current_code
        return mapping
    
    if root.left:
        generate_codes(root.left, current_code + "0", mapping)
    if root.right:
        generate_codes(root.right, current_code + "1", mapping)
        
    return mapping
# ==========================================
# Main Execution 
# ==========================================

def main():
    # if len(sys.argv) != 2:            #!remove before submission
    #     print("Usage: python 208066381_318793882_decompression.py <file.txt>")   #Change ID's
    #     sys.exit(1)
    # input_file = sys.argv[1]
    input_file = "208066381_318793882_compressed.txt"
    

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    output_filename = "208066381_318793882_decompressed.txt"    #Change ID's
    
    if not lines:
        with open(output_filename, "w", encoding="utf-8") as f:
            pass
        sys.exit(0)
    
    # ==========================================  
    # previously written code 
    encoded_text, postorder, inorder = lines
    postorder = postorder.rstrip().split(",")
    inorder = inorder.rstrip().split(",")
    
    rec_tree_root = build_from_traversals(postorder,inorder)
    code_map = generate_codes(rec_tree_root)
# ==========================================  
    decoded_text = "hello world" #!remove before submission
    # decoded_text = decompressed_content
# ==========================================
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(decoded_text + "\n")
    except IOError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)
    return code_map,encoded_text

if __name__ == "__main__":
    code_map,encoded_text = main()
    code_map = sorted(code_map.items(),key=lambda x:int(x[1]),reverse=True)
    print(code_map)
    list = [format(ord(char),"b") for char in encoded_text]
    bit_string = "".join(list)
    print(f"bit_string : {bit_string}\n")
    
    decoded_str_list = []
    encoding_list = []
    idx = 0
    found = False
    while idx < len(bit_string):
        for key,encoding in code_map:
            if bit_string[idx:].startswith(encoding):
                decoded_str_list.append(key)
                encoding_list.append(encoding)
                idx += len(encoding)
                break
    real_str_list = ["Lorem"," ","ipsum"," ","dolor"," ","sit"," ","amet"]
    
    print(real_str_list)
    print(decoded_str_list)
    print(encoding_list)
    