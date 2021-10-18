import threading
import socket
import time
import logging
from . import constants

logger = logging.getLogger(__name__)


class ProxyServer:
    def __init__(
            self,
            local_host: str,
            local_port: int,
            remote_host: str,
            remote_port: int,
            auto_start: bool = True
    ):
        self._local_host = local_host
        self._local_port = int(local_port)
        self._remote_host = remote_host
        self._remote_port = int(remote_port)

        self._socket = self._create_socket()
        self._active = False
        if auto_start:
            self.start_server()

    def _create_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self._local_host, self._local_port))
        server_socket.listen(5)

        logger.info(f"[*] TCP proxy listening on {self._local_host}:{server_socket.getsockname()[1]}")
        return server_socket

    def start_server(self):
        self._active = True

        while True:
            try:
                client_socket, addr = self._socket.accept()
                logger.info(f"[==>] Incoming tcp connection from client: {addr[0]}:{addr[1]}")

                proxy_thread = threading.Thread(
                    target=self.handler,
                    args=(
                        client_socket,
                    )
                )

                proxy_thread.start()
            except KeyboardInterrupt:
                self._active = False
                break

        self._socket.close()

    @staticmethod
    def receive_from(
            socket: socket.socket,
            timeout: int = constants.PROXY_SOCKET_READ_TIMEOUT,
            byte_size: int = constants.PROXY_SOCKET_READ_BYTE_SIZE
    ):
        # helper function to receive the complete data buffer

        data_buffer = b""
        try:
            # set connection timeout. Adjust as necessary
            socket.settimeout(timeout)

            # Keep receiving byte_size bytes of data until no more
            while True:
                data = socket.recv(byte_size)
                if not data:
                    break
                data_buffer += data

        except:
            pass

        return data_buffer

    @staticmethod
    def request_handler(buffer, from_client: bool):
        # placeholder function to modify request buffer
        print(buffer)
        print()
        return buffer

    def receive_send_data(self, from_socket: socket.socket, to_socket: socket.socket, from_client: bool) -> int:
        # receive data from client
        local_buffer = self.receive_from(from_socket)

        # send request to remotehost and reset timer
        if len(local_buffer):
            if from_client:
                from_ = 'client'
                to_ = 'remote'
            else:
                from_ = 'remote'
                to_ = 'client'

            logging.info(
                f"[==>] Sending {len(local_buffer)} bytes from {from_} to {to_}"
            )

            # modify request buffer if necessary
            local_buffer = self.request_handler(local_buffer, from_client)

            to_socket.sendall(local_buffer)

            return len(local_buffer)

        return 0

    def handler(self, client_socket, receive_first=False):
        connection_time = time.time()

        # create the remote socket
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to remotehost with remote socket
        remote_socket.connect((self._remote_host, self._remote_port))

        # receive data from remote host
        if receive_first:
            if self.receive_send_data(remote_socket, remote_socket):
                connection_time = time.time()

        while self._active:
            if self.receive_send_data(client_socket, remote_socket, True):
                connection_time = time.time()
            if self.receive_send_data(remote_socket, remote_socket, False):
                connection_time = time.time()

            # check if more than constants.PROXY_SOCKET_IDDLE_TIMEOUT secs has elapsed on an idle socket connection
            if (time.time() - connection_time > constants.PROXY_SOCKET_IDDLE_TIMEOUT) or (not self._active):
                client_socket.close()
                remote_socket.close()
                logging.info("[*] No more data. Closing connections")
                break
