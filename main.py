import sys
# import logging
# from dbproxy.proxy import TCPProxy
#
# logging.basicConfig(level=logging.INFO)
#
#
# if __name__ == '__main__':
#     # Create server and bind to set ip
#     myserver = TCPProxy('0.0.0.0', sys.argv[1], '0.0.0.0', 3307)
#
#     # activate the server until it is interrupted with ctrl+c
#     myserver.serve_forever()

import socket
TCP_IP = '0.0.0.0'
TCP_PORT = 3306

BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(5)

while True:
    client_socket, addr = s.accept()

    print(
        client_socket.recv(BUFFER_SIZE)
    )

s.close()
