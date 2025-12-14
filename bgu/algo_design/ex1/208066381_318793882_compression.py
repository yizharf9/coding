"""
Done by yizhar fahima   208066381
        eyal rothschild 318793882
"""
import sys

# ==========================================
# Implementation Area
# ==========================================
def compression(word):
    chars = word.split('')
    for char in chars:
        print(char)



# ==========================================
# Main Execution 
# ==========================================

def main():
    if len(sys.argv) != 2:
        print("Usage: python 208066381_318793882_compression.py 208066381_318793882_compressed.txt")   #Change ID's
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
            print(len(text))
            # print(len(chars))
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # output_filename = "208066381_318793882_compressed.txt"    #Change ID's #! real input file
    output_filename = "208066381_318793882_compressed.txt"    #Change ID's #! test input file
    
    if not text:
        with open(output_filename, "w", encoding="utf-8") as f:
            pass
        sys.exit(0)

# ==========================================  #! to be changed to real data !!!
    encoded_text = text
    postorder_list = ""              
    inorder_list = ""
# ==========================================

    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(encoded_text + "\n")
            f.write(",".join(postorder_list) + "\n")
            f.write(",".join(postorder_list) + "\n")
    except IOError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()