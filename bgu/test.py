"""
& and 
| or
^ xor
"""

def calculate_CRC_Tx(poly=0b1101111 ,data=0b10101111):
    print(f"data = {data:b}")
    poly_degree = get_degree(poly)
    data_after_shift = data << poly_degree
    data_after_shift_degree = get_degree(data_after_shift)
    poly_after_shift = poly << (data_after_shift_degree-poly_degree)
    print(f"shifted = {data_after_shift:b}")
    print(f"poly = {poly:b}")
    print(f"poly_after_shift = {poly_after_shift:b}")    
    
    division = poly_after_shift^data_after_shift
    print(f"division init. = {division:b}\n")
    
    # division_degree = get_degree(division)
    # poly_after_shift = poly << (division_degree-poly_degree)
    # division = division^poly_after_shift
    # print(f"division = {division:b}")
    
    
    count = 0
    while division > poly:
        count += 1
        division_degree = get_degree(division)
        poly_after_shift = poly << (division_degree-poly_degree)
        print(f"poly_after_shift = {poly_after_shift:b}\n")    
        division = division^poly_after_shift
        print(f"division {count} =       {division:b}")
    
    
    return division


def get_degree(poly=0b1101111):
    count = 0 
    while poly != 1 :
        poly = poly >> 1
        # print(f"{poly:b}")
        count +=1
    return count

result = calculate_CRC_Tx()
print(f"CRC = {result:b}")