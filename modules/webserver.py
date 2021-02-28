from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
#from config import Config
import time
import requests

class WebServer:
    """ Base class for web server. """
#    def __init__(self, config, hostname = None, port = None):
    def __init__(self, hostname = None, port = None):
        """ Instance constructor
        :params: hostname: Hostname for the web server to listen to (string)
        :params: port: Port for the web server to listen to (int)
        """

        # Get config parameters
        # Create config instance
#        config = Config()
#        config_webserver = config.getConfigParameter('webserver')

#        if config.webserver['default_hostname'] is None:
        if hostname is None:
            hostname = "localhost"
            print("Hostname not set. Setting hostname to \"{}\".".format(hostname))

#        if config.webserver('default_port') is None:
        if port is None:
            port = 8080
            print("Port not set. Setting port to \"{}\".".format(port))

        web_server = HTTPServer((hostname, port), WebServerHTTPRequestHandler)
        print("Server started on http://{}:{}".format(hostname, port))
        try:
            web_server.serve_forever()
        except KeyboardInterrupt:
            pass
        
        web_server.server_close()
        print("Server stopped.")

class WebServerHTTPRequestHandler(BaseHTTPRequestHandler):
    """ Web server HTTP request handler.
    :params BaseHTTPRequestHandler: 
    """
    def _set_headers(self, content_type = None):
        if content_type is None:
            content_type = "text/html"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_GET(self):
        """ Get request handling. """
        self._set_headers()
        self.wfile.write(bytes("<html><head><title>FenrisBox test</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_POST(self):
        """ POST request handling. """
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self._set_headers()
        response = BytesIO()
        response.write(b"POST request: ")
        response.write(b'Received: ')
        response.write(post_data)
        self.wfile.write(response.getvalue())

    def do_HEAD(self):
        """ HEAD request handling. """
        self._set_headers()