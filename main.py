from modules.webserver import WebServer
from modules.config import Config
#from modules.pcap import *
from modules.dnsserver import *

# Set hostname and port (not required)
hostname = '0.0.0.0'
port = 80


# Start of program
if __name__ == "__main__":

    # Create config instance
#    config = Config()
#    print(config.params.getProperty("webserver")["default_port"])
#    print(config.params)

    # Run the webserver on given hostname and port
    # If not set hostname nor port, the server will be set up using default parameters defined in config.yaml
#    webServer = WebServer(config, hostname, port)
#    webServer = WebServer(hostname, port)
#    webServer = WebServer()

    # Start DNS server
    dns_server = DNSServer()
    
    # Capture Pcaps
#    pcap = Pcap()
#    pcap.capturePcap()