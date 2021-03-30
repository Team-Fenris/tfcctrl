from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
#from config import Config
import requests
import threading
import time

class WebServer:
    """ Base class for web server. """
    def __init__(self, config, hostname = None, port = None):
        """ Instance constructor

        :params: config: Configuration parameters for the web server (yaml)

        :params: hostname: Hostname for the web server to listen to (string)

        :params: port: Port for the web server to listen to (int)
        """
        if hostname is None:
            hostname = config["default_hostname"]
            print(f"HTTP Server: Hostname not set. Setting hostname to \"{hostname}\"")

        if port is None:
            port = config["default_port"]
            print(f"HTTP Server: Port not set. Setting port to \"{port}\"")

        web_server = HTTPServer((hostname, port), WebServerHTTPRequestHandler)
        print("------------------------------------------------------------------------------------------------------")
        if config["threading"]:
            thread = threading.Thread(target=web_server.serve_forever, name=config["params_name"], daemon=True)
            thread.start()

            if config["debug"]:
                sleep_timer = config["sleep"]
                print(f"HTTP Server: Debug detected. Sleeping for {sleep_timer} seconds before ending thread.")
                print("------------------------------------------------------------------------------------------------------")
                time.sleep(sleep_timer)
        else:
            try:
                print(f"Server listening on http://{hostname}:{port}")
                web_server.serve_forever()
            except KeyboardInterrupt:
                pass

            web_server.server_close()

        print("HTTP Server: Server stopped.")

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
        self.wfile.write(b"<html><head><title>FenrisBox test</title></head>")
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(b"<body>")
        self.wfile.write(b"<p>This is an example web server.</p>")
        self.wfile.write(b"</body></html>")

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