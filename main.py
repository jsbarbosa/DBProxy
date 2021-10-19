import sys
import logging
from dbproxy.proxy2 import TCPServer, SockHandler, TCPProxy

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    # Create server and bind to set ip
    myserver = TCPProxy('0.0.0.0', sys.argv[1], '0.0.0.0', 3306)

    # activate the server until it is interrupted with ctrl+c
    myserver.serve_forever()
