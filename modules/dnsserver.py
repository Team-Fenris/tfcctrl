import datetime
from dnslib import *
import socketserver
import socket
import ssl
import threading
import traceback

# Set interrim variables
debug = True
param_threading = True
param_sleeping = 100
params_name = 'Threaded DNS server'

class DNSServer:
    """ Base class for DNS server. """
    def __init__(self, hostname = None, port = None):
        """ Instance constructor

        :params: hostname: Hostname
    
        :params: port: Port
        """

        if hostname is None:
            hostname = "0.0.0.0"
            print(f"DNS Server: Hostname not set. Setting hostname to \"{hostname}\"")

        if port is None:
            port = 53
            print(f"DNS Server: Port not set. Setting port to \"{port}\"")

        dns_server = socketserver.ThreadingUDPServer(('', port), UDPRequestHandler)
        print("------------------------------------------------------------------------------------------------------")
        if param_threading:
            thread = threading.Thread(target=dns_server.serve_forever, name=params_name, daemon=True)
            thread.start()

            if debug:
                print(f"DNS Server: Debug detected. Sleeping for {param_sleeping} seconds before ending thread.")
                print("------------------------------------------------------------------------------------------------------")
                time.sleep(param_sleeping)
        else:
            try:
                dns_server.serve_forever()
            except KeyboardInterrupt:
                pass

            dns_server.server_close()

        print("Server stopped.")


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
    def response(data):
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
            reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q, a=RR(query_name,rdata=A("127.0.0.1")))

            if debug:
                print(f"query_name: {query_name} | query_str: {query_str} | query_type: {query_type} | dns_record_type: {dns_record_type}\n")

                print(f"DNS reply: {reply}\n")
                print("------------------------------------------------------------------------------------------------------")
            return reply.pack()
        else:
            return None

    def handle(self):
        """ Do all work required to service a request. """
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f"{self.__class__.__name__[:3]} request {now} ({self.client_address[0]} {self.client_address[1]})")
        try:
            data = self.get_data()
            self.send_data(self.response(data))
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