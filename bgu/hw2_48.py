"""
& and 
| or
^ xor
"""

def calculate_CRC_Tx(data=0b10101111,poly=0b1101111,print_flag = False):
    if print_flag :
        print(f"data = {data:b}")
        print(f"data = {data:b}")
    poly_degree = get_degree(poly)
    data_after_shift = data << poly_degree
    data_after_shift_degree = get_degree(data_after_shift)
    poly_after_shift = poly << (data_after_shift_degree-poly_degree)
    if print_flag :
        print(f"shifted = {data_after_shift:b}")
        print(f"poly = {poly:b}")
        print(f"poly_after_shift = {poly_after_shift:b}")    
    
    division = poly_after_shift^data_after_shift
    
    if print_flag :
        print(f"division init. = {division:b}\n")
    
    count = 0
    while division > poly:
        count += 1
        division_degree = get_degree(division)
        poly_after_shift = poly << (division_degree-poly_degree)
        if print_flag :
            print(f"poly_after_shift = {poly_after_shift:b}\n")    
            print(f"division {count} =       {division:b}")
        division = division^poly_after_shift
    
    return division


def get_degree(poly=0b1101111):
    count = 0 
    while poly != 1 :
        poly = poly >> 1
        count +=1
    return count

# result = calculate_CRC_Tx()
# print(f"CRC = {result:b}")

def calculate_CRC_Rx(data=0b10101111,poly=0b1101111,CRC = 0b010010):
    CRC_calc = calculate_CRC_Tx(data,poly)
    return CRC == CRC_calc 

# print(calculate_CRC_Rx())

def first_check():
    data = 0xAF
    poly = 0x6F
    print("Check 0-bit error CRC: ", end="")
    print( calculate_CRC_Rx(data, poly, calculate_CRC_Tx(data, poly)) == True )
    print("Check 1-bit error CRC: ", end="")
    print( calculate_CRC_Rx(data ^ 1, poly, calculate_CRC_Tx(data, poly)) == False )
    print("Check 2-bit error CRC: ", end="")
    print( calculate_CRC_Rx(data ^ 3, poly, calculate_CRC_Tx(data, poly)) == False )
    
first_check()


def calculate_Hamming74_Tx(data = 'Z',print_flag = False):
    if print_flag : 
        print(f"data = {data}")
    if print_flag : 
        print(f"data in bin = {ord(data):b}")
    data_bin = ord(data)
    encoded_low = data_bin & 0x0F
    encoded_high = (data_bin & 0xF0 ) >> 4
    # 0 [p1] [p2] [d1] [p3] [d2] [d3]  [d4]
    # [d1] [d2] [d3] [d4]
    if print_flag : 
        print(f"encoded_low = {encoded_low:b}")
    if print_flag : 
        print(f"encoded_high = {encoded_high:b}")
    
    p1_high,p2_high,p3_high = parity_bits(encoded_high)
    p1_low,p2_low,p3_low = parity_bits(encoded_low)
    
    encoded_high = encode_parity(encoded_high,p1_high,p2_high,p3_high)
    encoded_low = encode_parity(encoded_low,p1_low,p2_low,p3_low)
    
    return encoded_high,encoded_low

def parity_bits(data,print_flag = False):
    # [d1] [d2] d3 [d4] <= LSB
    ext_p1 = 0b1101
    p1 = (ext_p1 & data).bit_count() & 1
    if print_flag :
        print(f"p1 = {p1}")
    
    # [d1] d2 [d3] [d4] <= LSB
    ext_p2 = 0b1011    
    p2 = (ext_p2 & data).bit_count() & 1
    if print_flag :
        print(f"p2 = {p2}")
    
    # d1 [d2] [d3] [d4] <= LSB
    ext_p3 = 0b0111
    p3 = (ext_p3 & data).bit_count() & 1
    if print_flag :
        print(f"p3 = {p3}\n")
    
    return p1,p2,p3

def encode_parity(data = 0b1101,p1 = 1,p2 = 0,p3 = 1,print_flag= False):
    # 0 [p1] [p2] [d1] [p3] [d2] [d3]  [d4]
    if print_flag :
        print(f"data = {data:b}")
    p1 = p1 << 6
    if print_flag :
        print(f"p1 = {p1:b}")
    p2 = p2 << 5
    if print_flag :
        print(f"p2 = {p2:b}")
    d1 = (data >> 3) << 4
    if print_flag :
        print(f"d1 = {d1:b}")
    p3 = p3 << 3
    if print_flag :
        print(f"p3 = {p3:b}")
    d2d3d4 = data & 0b111
    if print_flag :
        print(f"d2d3d4 = {d2d3d4:b}\n")
    return p1+ p2 + p3 + d1 + d2d3d4

def calculate_Hamming74_Rx(encoded_high = 0b0110101, encoded_low = 0b1001010):
    # encoded_high = 0b0100101, encoded_low = 0b1011010
    decoded_high = decode_parity(encoded_high) << 4
    decoded_low = decode_parity(encoded_low)
    decoded_data = decoded_high + decoded_low
    return chr(decoded_data)

def decode_parity(data = 0b1111010,print_flag = False):
    # 0 [p1] [p2] [d1] [p3] [d2] [d3]  [d4]
    if print_flag :
        print(f"data = {data:b}")
    s1 = (data & 0b01010101).bit_count() & 1
    if print_flag :
        print(f"s1 = {s1:b}")
    s2 = (data & 0b00110011).bit_count() & 1
    if print_flag :
        print(f"s2 = {s2:b}")
    s3 = (data & 0b00001111).bit_count() & 1
    if print_flag :
        print(f"s3 = {s3:b}")
    s = s1 + (s2 << 1) + (s3 << 2)
    # % [p1] [p2] [d1] [p3] [d2] [d3]  [d4]
    data_fixed = data ^ ((0b10000000) >> s)
    if print_flag :
        print(f"data_fixed = {data_fixed:b}")
    d1 = (data_fixed & 0b10000) >> 1
    if print_flag :
        print(f"d1 = {d1:b}")
    d2d3d4 = data_fixed & 0b111
    if print_flag :
        print(f"d2d3d4 = {d2d3d4:b}")
    return (d1 + d2d3d4)

# high,low = calculate_Hamming74_Tx()
# print(f"high = {high:b}")
# print(f"low = {low:b}")

# high = high ^ 0b0100
# low = low ^ 0b0010

# print("-" * 50 )
# result = calculate_Hamming74_Rx(high,low)
# print(f"decoded fixed data = {result}")


def second_check():
    data = "Z"
    high, low = calculate_Hamming74_Tx(data)
    print("Check 0-bit error Hamming: ", end="")
    print( calculate_Hamming74_Rx(high, low) == data )
    print("Check 1-bit error Hamming: ", end="")
    print( calculate_Hamming74_Rx(high ^ 1, low) == data )
    print("Check 2-bit error Hamming: ", end="")
    print( calculate_Hamming74_Rx(high ^ 3, low) != data )

second_check()