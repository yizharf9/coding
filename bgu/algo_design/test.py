from collections import deque
from typing import Deque, Tuple, List, Dict

class Node():
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

def inorder(root):
    if root.right is None and root.left is None:
        print(f"leaf : {root.value[0]} (Freq: {root.value[1]})")
        return

    if root.left is not None:
        inorder(root.left)
    if root.right is not None :
        inorder(root.right)

def get_char_encoding(root: Node, encoded_value: str = "", encoding: dict[str, str] = None) -> dict[str, str]:
    if encoding is None:
        encoding = {}

    if root.left is None and root.right is None:
        char = root.value[0]
        encoding[char] = encoded_value
        return encoding
        
    if root.left is not None:
        get_char_encoding(root.left, encoded_value + "0", encoding)
        
    if root.right is not None:
        get_char_encoding(root.right, encoded_value + "1", encoding)
        
    return encoding

def get_min_node(q1: Deque[Node], q2: Deque[Node]) -> Node:
    if not q1 and not q2:
        raise ValueError("Both queues are empty; cannot extract.")
    
    if not q2:
        return q1.popleft()
    
    if not q1:
        return q2.popleft()
    
    freq1 = q1[0].value[1]
    freq2 = q2[0].value[1]
    
    if freq1 <= freq2:
        return q1.popleft()
    else:
        return q2.popleft()

def extract_2_min(q1: deque[Node], q2: deque[Node]) -> tuple[Node, Node]:
    min1 = get_min_node(q1, q2)
    min2 = get_min_node(q1, q2)
    return min1, min2

def print_tree(root: Node, prefix: str = "", is_left: bool = True):
    if root is None:
        return

    if root.right is not None:
        new_prefix = prefix + ("|   " if is_left else "    ")
        print_tree(root.right, new_prefix, False)

    node_value_str = f"'{repr(root.value[0])}' ({root.value[1]})"
    
    print(prefix + ("└── " if is_left else "┌── ") + node_value_str)

    if root.left is not None:
        new_prefix = prefix + ("    " if is_left else "|   ")
        print_tree(root.left, new_prefix, True)

if __name__ == "__main__":
    char_tokens = False 
    
    try:
        with open("./data.txt","r") as f:
            text = f.read()[:50]
    except FileNotFoundError:
        print("Error: data.txt not found. Using sample text instead.")
        text = "this is a sample text for huffman coding"
    
    if not char_tokens:
        text = text.split(sep=" ")
    
    counter = {}
    for char in text:
        if counter.get(char,0) == 0 :
            counter[char] = 1
        else :
            counter[char] += 1
        
    
    sorted_items = sorted(counter.items(), key=lambda x: x[1])
    for key, val in sorted_items:
        print(f"'{repr(key)}': {val}", end=' | ')
    print('\n')

    q1: Deque[Node] = deque([Node(count) for count in sorted_items]) 
    q2: Deque[Node] = deque() 

    while len(q1) + len(q2) > 1:
        min1, min2 = extract_2_min(q1, q2)
        left = min([min1, min2], key=lambda x: x.value[1])
        right = max([min1, min2], key=lambda x: x.value[1])
        
        c = Node((min1.value[0] + min2.value[0], min1.value[1] + min2.value[1]), left=left, right=right)
        q2.append(c)

    root = q1.pop() if q1 else q2.pop()

    print_tree(root)

    encoding: Dict[str, str] = get_char_encoding(root=root, encoding={})
    
    for char, code in sorted(encoding.items(), key=lambda item: len(item[1])):
        print(f"'{repr(char)}': {code}")