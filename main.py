from modules.webserver import WebServer
from modules.pcap import *
from modules.config import Config
from modules.dnsserver import *

# Start of program
if __name__ == "__main__":

    # Create config instance
    config = Config()

    # Hand over config parameters and start the HTTP server
#    web_server = WebServer(config.params.getProperty("webserver"))

    # Hand over config parameters and start the DNS server
#    dns_server = DNSServer(config.params.getProperty("dnsserver"))
    
    # Capture Pcaps
#    pcap = Pcap()
#    pcap.capturePcap()