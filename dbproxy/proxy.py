from socketserver import BaseRequestHandler, TCPServer, StreamRequestHandler, ForkingTCPServer
import socket
from . import constants
import logging
from typing import Union
import time

logger = logging.getLogger(__name__)


class SockHandler(BaseRequestHandler):
    """
    Request Handler for the proxy server.
    Instantiated once time for each connection, and must
    override the handle() method for client communication.
    """

    def setup(self):
        self._host = self.server._remote_host
        self._port = self.server._remote_port

        self.request.settimeout(constants.PROXY_SOCKET_READ_TIMEOUT)
        self.request.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, constants.PROXY_SOCKET_KEEPALIVE)
#        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, constants.PROXY_SOCKET_KEEPIDLE)
        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, constants.PROXY_SOCKET_KEEPINTVL)
        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, constants.PROXY_KEEPCNT)

        self.request.setblocking(0)  # make socket non blocking
        logger.info(f"SockHandler setup to '{self._host}:{self._port}'")

    @staticmethod
    def get_data(socket: socket.socket):
        total_data = []  # total data partwise in an array

        begin = time.time() # beginning time

        while True:
            # if you got some data, then break after timeout
            if total_data and time.time() - begin > constants.PROXY_SOCKET_READ_TIMEOUT:
                break

            # if you got no data at all, wait a little longer, twice the timeout
            elif time.time() - begin > constants.PROXY_SOCKET_READ_TIMEOUT * 2:
                break

            # recv something
            try:
                data = socket.recv(constants.PROXY_SOCKET_READ_BYTE_SIZE)
                if data:
                    total_data.append(data)
                    # change the beginning time for measurement
                    begin = time.time()
                else:
                    # sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except OSError:
                pass

        # join all parts to make final string
        return b''.join(total_data)

    @staticmethod
    def write_data(socket: socket.socket, data: bytes):
        for i in range(0, len(data), constants.PROXY_SOCKET_READ_BYTE_SIZE):
            temp = data[i: i + constants.PROXY_SOCKET_READ_BYTE_SIZE]
            socket.send(
                temp
            )

    def handle(self):
        data = self.get_data(self.request)

        # self.request is the TCP socket connected to the client
        logging.info("Passing data from: {}".format(self.client_address[0]))
        logging.info(data)

        if data:
            # Create a socket to the localhost server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(0)
            sock.settimeout(constants.PROXY_SOCKET_READ_TIMEOUT)

            # Try to connect to the server and send data
            try:
                sock.connect((self._host, self._port))
                sock.sendall(data)

                while True:
                    # Receive data from the server
                    from_server = self.get_data(sock)
                    logging.info("From server")
                    logging.info(from_server)
                    if from_server:
                        self.request.sendall(from_server)
                    else:
                        break
            finally:
                sock.close()


class TCPProxy(TCPServer):
    def __init__(
            self,
            local_host: str,
            local_port: Union[int, str],
            remote_host: str,
            remote_port: Union[int, str],
            *args,
            **kwargs
    ):
        self._remote_host = remote_host
        self._remote_port = int(remote_port)

        super(TCPProxy, self).__init__(
            (local_host, int(local_port)),
            SockHandler,
            *args,
            bind_and_activate=True,
            **kwargs
        )

        logger.info(f"TCP Proxy started on '{local_host}:{local_port}'")

    def serve_forever(self, *args, **kwargs):
        try:
            super(TCPProxy, self).serve_forever(*args, **kwargs)
        except KeyboardInterrupt:
            self.shutdown()
