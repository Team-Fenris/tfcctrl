import datetime
from dnslib import *
from modules.config import Config
from modules.api import FenrisApi
import socketserver
import socket
import ssl
import threading
import traceback

# Constants
CONFIG=Config()
API_URL=CONFIG.params.getProperty("dnsserver")["api_url"]
CFG_PARAM=CONFIG.params.getProperty("dnsserver")
API=FenrisApi()

class FenrisDNSServer:
    """ Base class for DNS server. """
    def __init__(self, listener_ip = None, port = None):
        """ Instance constructor

        :params: config: Configuration parameters (yaml)

        :params: listener_ip: Listener IP address (string)
    
        :params: port: Listener port (int)
        """
        self.listener_ip = listener_ip
        self.port = port
        if self.listener_ip is None:
            self.listener_ip = CFG_PARAM["listener_ip"]
#            print(f"DNS Server: Listener IP not set. Setting listener IP to \"{self.listener_ip}\"")

        if self.port is None:
            self.port = CFG_PARAM["listener_port"]
#            print(f"DNS Server: Port not set. Setting port to \"{self.port}\"")       

    def start(self):
        print(f"FenrisDNSServer: Starting DNS server on {self.listener_ip}:{self.port}")
        self.dnsd = socketserver.ThreadingUDPServer(('', self.port), UDPRequestHandler)
        self.thread = threading.Thread(target=self.dnsd.serve_forever, daemon=True)
        self.thread.start()

class BaseRequestHandler(socketserver.BaseRequestHandler):
    """ DNS server base request handler.

    :params BaseHTTPRequestHandler: inherited from socketserver.BaseRequestHandler
    """
    def get_data(self):
        """ Get request handling. """
        raise NotImplementedError

    def send_data(self, data):
        """ Send data handling. """
        raise NotImplementedError

    @staticmethod
    def response(data, api_data = None):
        """ Send response reply. """

        # Parse the DNS request and set reply
        request = DNSRecord.parse(data)

        # Set query info
        query_name = request.q.qname
        query_str = str(query_name)
        query_type = request.q.qtype
        dns_record_type = QTYPE[query_type]

        # Check if the DNS record is a A-record
        if dns_record_type == "A":
            # Create and return reply
            reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q, a=RR(query_name,rdata=A(CFG_PARAM["return_ip"])))

            if CFG_PARAM["api"]:

                # Remove last dot in domain name (if any)
                if query_str.endswith('.'):
                    query_str = query_str[:-1]

                api_data['query_str'] = query_str
                api_data['query_type'] = query_type
                api_data['record_type'] = dns_record_type
#                api_data['dns_reply'] = reply.pack()
                API.send(API_URL, api_data)

                if CFG_PARAM["debug"]:
                    print(f"API_DATA FULL: {api_data}")

            if CFG_PARAM["debug"]:
                print(f"query_name: {query_name} | query_str: {query_str} | query_type: {query_type} | dns_record_type: {dns_record_type}\n")
                print(f"DNS reply:\n{reply}\n")
                print("------------------------------------------------------------------------------------------------------")

            return reply.pack()
        else:
            return None

    def handle(self):
        """ Do all work required to service a request. """
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f"{self.__class__.__name__[:3]} request {now} ({self.client_address[0]} {self.client_address[1]})")

        if CFG_PARAM["api"]:
            api_data = {
                'from_host_generic_ip': self.client_address[0],
                'from_port': self.client_address[1],
                'dns': self.__class__.__name__[:3]
            }
            print("API DATA:", api_data)
        else:
            api_data = None

        try:
            data = self.get_data()
            self.send_data(self.response(data, api_data))
        except Exception:
            pass

class UDPRequestHandler(BaseRequestHandler):
    """ DNS server UDP request handler.

    :params: BaseRequestHandler:
    """
    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)