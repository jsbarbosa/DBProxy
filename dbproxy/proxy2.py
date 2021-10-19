from socketserver import BaseRequestHandler, TCPServer, StreamRequestHandler, ForkingTCPServer
from socket import socket, AF_INET, SOCK_STREAM
from . import constants
import logging
from typing import Union

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
        logger.info(f"SockHandler setup to '{self._host}:{self._port}'")

    @staticmethod
    def get_data(request, until: int = None):
        full_data = b''
        if until is not None:
            return b''.join(
                [request.recv(constants.PROXY_SOCKET_READ_BYTE_SIZE) for i in range(until)]
            )

        while True:
            try:
                data = request.recv(constants.PROXY_SOCKET_READ_BYTE_SIZE)

                if not data:
                    break

                full_data += data

            except OSError:
                break

        return full_data

    @staticmethod
    def write_data(socket: socket, data: bytes):
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
            sock = socket(AF_INET, SOCK_STREAM)

            # Try to connect to the server and send data
            try:
                sock.connect((self._host, self._port))
                sock.settimeout(constants.PROXY_SOCKET_READ_TIMEOUT)

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
