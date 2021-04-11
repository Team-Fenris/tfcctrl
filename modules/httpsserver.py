import ssl

from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from hashlib import sha256
import threading
import time
import datetime

from modules.config import Config
from modules.api import FenrisApi

# Constants
CONFIG=Config()
API_URL=CONFIG.params.getProperty("httpsserver")["api_url"]
API=FenrisApi()
CFG_PARAM=CONFIG.params.getProperty("httpsserver")

class RequestHandlerHTTPS(BaseHTTPRequestHandler):
    """ Web server HTTPS request handler.
    Inheriting from BaseHTTPRequestHandler.
    """
    def generateAndSendAPIData(self):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        # Hack for fixing request issue for localhost
        if self.headers.get('Host') == 'localhost':
            host_generic_ip = '127.0.0.1'
        else:
            host_generic_ip = self.headers.get('Host')
            
        api_data = {
            "host_generic_ip": host_generic_ip,
            "user_agent": self.headers.get('User-Agent'),
            "accept": self.headers.get('Accept'),
            "accept_language": self.headers.get('Accept-Language'),
            "accept_encoding": self.headers.get('Accept-Encoding'),
            "https_connection": self.headers.get('Connection'),
            "https_command": self.command,
            "https_path": self.path,
            "request_version": self.request_version,
            "request_timestamp": now
        }

        API.send(API_URL, api_data)
        if CFG_PARAM["debug"]:
            print("HTTPS API DATA:", api_data)

    def do_GET(self):
        self.send_response(200)
        if CFG_PARAM["api"]:
            self.generateAndSendAPIData()
        self.end_headers()

    def do_POST(self):
        self.send_response(200)
        if CFG_PARAM["api"]:
            self.generateAndSendAPIData()
        self.end_headers()

class FenrisHTTPSServer:
    """ Base class for HTTPS server. """
    def __init__(self, listener_ip = None, port = None):
        """ Instance constructor

        :params: config: Configuration parameters (yaml)

        :params: listener_ip: Listener IP address (string)

        :params: port: Listener port (int)
        """
        self.listener_ip = listener_ip
        self.port = port
        self.crt_file = CFG_PARAM["crt_file"]
        if self.listener_ip is None:
            self.listener_ip = CFG_PARAM["listener_ip"]
#            print(f"HTTPS Server: Listener IP not set. Setting listener IP to \"{self.listener_ip}\"")

        if self.port is None:
            self.port = CFG_PARAM["listener_port"]
#            print(f"HTTPS Server: Port not set. Setting port to \"{self.port}\"")

    def start(self):
        print(f"FenrisHTTPSServer: Starting HTTPS server on {self.listener_ip}:{self.port}")
        self.httpd = HTTPServer((self.listener_ip, self.port), RequestHandlerHTTPS)
        self.httpd.socket = ssl.wrap_socket(self.httpd.socket, server_side=True, certfile='localhost.pem', ssl_version=ssl.PROTOCOL_TLS)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
