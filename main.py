from modules.webserver import WebServer
from modules.config import *

# Set hostname and port (not required)
hostname = 'localhost'
port = 8090


# Start of program
if __name__ == "__main__":

    # Create config instance
#    config = Config()

    # Run the webserver on given hostname and port
    # If not set hostname nor port, the server will be set up using default parameters defined in config.yaml
#    webServer = WebServer(config, hostname, port)
    webServer = WebServer(hostname, port)