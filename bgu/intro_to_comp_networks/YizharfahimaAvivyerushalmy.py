import socket
try :
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_IP_as_string = "132.72.107.37"
    port_as_integer = 10000
    message = "Yizhar Fahima Aviv Yerushalmy"

    sock.connect((server_IP_as_string, port_as_integer))

    sock.sendall(bytes(message, 'utf-8'))

    data = sock.recv(1000)

    print(data.decode())

    sock.close()
finally :
    raise TimeoutError(f"no response from server at : {server_IP_as_string} at port : {port_as_integer}")