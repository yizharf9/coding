from collections import deque

class Node():
    def __init__(self,value,left = None,right = None):
        self.value = value
        self.left = left
        self.right = right

def inorder(root):
    
    if root.right is None and root.left is None:
        print(f"{root.value}")
    if root.right is not None :
        inorder(root.right)    
    if root.left is not None:
        inorder(root.left)

def get_char_encoding(root: Node, encoded_value: str = "", encoding: dict[str, str] = None) -> dict[str, str]:
    if encoding is None:
        encoding = {}

    if root.left is None and root.right is None:
        char = root.value[0]
        encoding[char] = encoded_value
        return encoding # Stop recursion here
        
    if root.left is not None:
        get_char_encoding(root.left, encoded_value + "0", encoding)
        
    if root.right is not None:
        get_char_encoding(root.right, encoded_value + "1", encoding)
        
    return encoding

def extract_2_min(q1: deque[Node], q2: deque[Node]) -> tuple[Node, Node]:    
    
    def get_min_node(q1: deque[Node], q2: deque[Node]) -> Node:
        # Check for empty states
        if not q1 and not q2:
            raise ValueError("Both queues are empty; cannot extract.")
        
        # Scenario 1: Only q1 has nodes -> Pop from q1
        if not q2:
            return q1.popleft()
        
        # Scenario 2: Only q2 has nodes -> Pop from q2
        if not q1:
            return q2.popleft()
        
        # Scenario 3: Both queues have nodes - Compare fronts (index 0)
        freq1 = q1[0].value[1]
        freq2 = q2[0].value[1]
        
        # Extract the node with the smaller or equal frequency
        if freq1 <= freq2:
            return q1.popleft()
        else:
            return q2.popleft()

    # Extract the first minimum node
    min1 = get_min_node(q1, q2)
    
    # Extract the second minimum node (the queues are now one node smaller)
    min2 = get_min_node(q1, q2)
    
    return min1, min2

if __name__ == "__main__":
    with open("./data.txt","r") as f:
        text = f.read()

    counter = {}
    for char in text:
        if counter.get(char,0) == 0 :
            counter[char] = 1
        else :
            counter[char] += 1

    for key,val in sorted(counter.items(),key=lambda x : x [1]):
        print(key,val,end=' | ')
    print()

    q1 = deque([Node(count) for count in sorted(counter.items(), key=lambda x : x [1])]) 
    q2 = deque() 

    while len(q1) + len(q2) > 1 :
        min1,min2 = extract_2_min(q1,q2)
        left = min([min1,min2],key=lambda x : x.value[1])
        right = max([min1,min2],key=lambda x : x.value[1])
        c = Node((min1.value[0]+min2.value[0],min1.value[1]+min2.value[1]),left=left,right=right)
        # print(f"\nq1,q2 : {len(q1),len(q2)}")
        # print(f"min1,min2:{min1.value,min2.value}")
        # print(c.value)    
        q2.append(c)

    root = q2.pop()
    # print(f"root:{root.value}")
    inorder(root)
    # encoding = {}
    # encoding = get_char_encoding(root=root,encoding=encoding)
    # print(encoding)
