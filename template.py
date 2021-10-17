#a simple tcp proxy
import sys
import threading
import socket
import hexdump
import time
global localhost
global localport
global remotehost
global remoteport
global receive_first
receive_first = False
def usage():
    print("                                                                           ")
    print("************************ Python TCP Proxy *********************************")
    print("Usage: python3 ch2_tcpproxy_example.py 127.0.0.1 21 ftp.example.com 21 True")
    print("1st arg                                                   localhost address")
    print("2nd arg                                                      localhost port")
    print("3rd arg                                                  remotehost address")
    print("4th arg                                                         remote port")
    print("5th arg                                 receive from remote (True or False)")
    print("                                                                           ")
    sys.exit(0)
def server_loop(localhost, localport, remotehost, remoteport, receive_first):
    #create the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#bind the server socket
    try:
        server_socket.bind((localhost, localport))
    except:
        print(f"[!] Error binding with {localhost}:{server_socket.getsockname()[1]}")
        sys.exit(0)
#listen to incoming connections
    server_socket.listen(5)
    print(f"[*] TCP proxy listening on {localhost}:{server_socket.getsockname()[1]}")
#accept incoming connections and spawn a proxy thread with client socket
    while True:
        client_socket, addr = server_socket.accept()
        print(f"[==>] Incoming tcp connection from client: {addr[0]}:{addr[1]}")
        proxy_thread = threading.Thread(target=proxy_handler, args=(
            client_socket, remotehost, remoteport, receive_first)
        )
        proxy_thread.start()
def proxy_handler(client_socket, remotehost, remoteport, receive_first):
#Start a timer
    connectionTime = time.time()
#helper function to receive the complete data buffer
    def receive_from(socket):
        try:
            #set connection timeout. Adjust as necessary
            socket.settimeout(2)
#Keep receiving 4096 bytes of data until no more
            data_buffer = b""
while True:
                data = socket.recv(1024)
                if not data:
                    break
                data_buffer += data
        except:
            #print("[!] Socket Error")
            pass
return data_buffer
#placeholder function to modify request buffer
    def request_handler(buffer):
        return buffer
#placeholder function to modify response buffer
    def response_handler(buffer):
        return buffer
#create the remote socket
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #connect to remotehost with remote socket
    remote_socket.connect((remotehost, remoteport))
#receive data from remote host
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump.hexdump(remote_buffer)
#modify response buffer if necessary
        remote_buffer = response_handler(remote_buffer)
#send response to client and reset timer
        if len(remote_buffer):
            client_socket.send(remote_buffer)
            connectionTime = time.time()
            print(f"[==>] Sending {len(remote_buffer)} bytes from remotehost {remotehost}:{remoteport} to client\n")
while True:
        #receive data from client
        local_buffer = receive_from(client_socket)
        hexdump.hexdump(local_buffer)
#modify request buffer if necessary
        local_buffer = request_handler(local_buffer)
#send request to remotehost and reset timer
        if len(local_buffer):
            remote_socket.send(local_buffer)
            connectionTime = time.time()
            print(f"[==>] Sending {len(local_buffer)} bytes from client to remotehost {remotehost}:{remoteport}\n")
#receive data from remote host
        remote_buffer = receive_from(remote_socket)
        hexdump.hexdump(remote_buffer)
#modify response buffer if necessary
        remote_buffer = response_handler(remote_buffer)
#send response to client and reset timer
        if len(remote_buffer):
            client_socket.send(remote_buffer)
            connectionTime = time.time()
            print(f"[==>] Sending {len(remote_buffer)} bytes from remotehost {remotehost}:{remoteport} to client\n")
#check if more than 60 secs has elpased on an idle socket connection
if time.time() - connectionTime > 60:
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections")
            break
def main():
    #define global vars
    global localhost
    global localport
    global remotehost
    global remoteport
    global receive_first
#check and validate args
    if len(sys.argv[1:]) != 5:
        usage()
    else:
        localhost = sys.argv[1]
        remotehost = sys.argv[3]
if int(sys.argv[2]) >= 0 and int(sys.argv[2]) < 65536:
            localport = int(sys.argv[2])
        else:
            print("[!] Invalid Arguments")
            usage()
if int(sys.argv[4]) > 0 and int(sys.argv[4]) < 65536:
            remoteport = int(sys.argv[4])
        else:
            print("[!] Invalid Arguments")
            usage()
if sys.argv[5] in ["true", "True"]:
            receive_first = True
        elif sys.argv[5] in ["false", "False"]:
            receive_first = False
        else:
            print("[!] Invalid Arguments")
            usage()
server_loop(
            localhost,
            localport,
            remotehost,
            remoteport,
            receive_first
        )
main()
