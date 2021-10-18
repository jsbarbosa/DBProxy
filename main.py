import sys
import logging
from dbproxy.proxy import ProxyServer

logging.basicConfig(level=logging.INFO)
proxy = ProxyServer("127.0.0.1", sys.argv[1], "0.0.0.0", 8000)