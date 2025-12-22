import sys
from typing import List, Union

LIST_DELIMITER = '\0'
OUTPUT_FILENAME = "208066381_318793882_decompressed.txt"

class Node:
    def __init__(self, value: Union[str, int], freq: int, left=None, right=None):
        self.value = value
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None

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
    
    right_subtree = inorder[root_idx+1:]
    right_subtree_root = build_from_traversals(postorder, right_subtree) if right_subtree else None
    
    left_subtree = inorder[:root_idx]
    left_subtree_root = build_from_traversals(postorder, left_subtree) if left_subtree else None
    
    root = Node(root_val, freq=0)
    root.left = left_subtree_root
    root.right = right_subtree_root
    
    return root 

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <file.txt>")
        sys.exit(1)
    
    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="latin-1") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    if not lines:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            pass
        sys.exit(0)
    
    try:
        inorder_str = lines[-1].rstrip('\n\r')
        postorder_str = lines[-2].rstrip('\n\r')
        
        compressed_content_lines = lines[:-2]
        compressed_content = "".join(compressed_content_lines)
        
        if compressed_content.endswith('\n'):
            compressed_content = compressed_content[:-1]
            
        postorder = postorder_str.split(LIST_DELIMITER)
        inorder = inorder_str.split(LIST_DELIMITER)
        
    except IndexError:
        print("Error: Input file format incorrect.")
        sys.exit(1)
    
    postorder = [x for x in postorder if x != ""]
    inorder = [x for x in inorder if x != ""]

    rec_tree_root = build_from_traversals(postorder, inorder)
    
    if rec_tree_root is None:
        print("Error: Failed to reconstruct Huffman tree.")
        sys.exit(1)

    padding_char = compressed_content[0]
    padding_count = ord(padding_char)
    
    raw_data = compressed_content[1:]
    
    bit_string_parts = []
    for char in raw_data:
        bit_string_parts.append(f"{ord(char):08b}")
    
    full_bit_string = "".join(bit_string_parts)
    
    if padding_count > 0:
        full_bit_string = full_bit_string[:-padding_count]

    decoded_chars = []
    current_node = rec_tree_root
    
    for bit in full_bit_string:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
            
        if current_node and current_node.is_leaf():
            decoded_chars.append(current_node.value)
            current_node = rec_tree_root

    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write("".join(decoded_chars))
    except IOError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()