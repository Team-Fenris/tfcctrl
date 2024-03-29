# Parts of code reproduced from: https://github.com/fireeye/flare-fakenet-ng/blob/master/fakenet/diverters/winutil.py
#import ctypes
import os
import datetime
import pydivert
import pydivert.consts
import socket
import struct
import time
import json
from hexdump import hexdump
from modules.config import Config
from modules.api import FenrisApi

from scapy.utils import PcapWriter as _PcapWriter
from scapy.layers.inet import IP as _IP
from ctypes import *
from ctypes.wintypes import *
from socket import *

# Constants

## Network
TCP_TABLE_OWNER_PID_ALL = 5
UDP_TABLE_OWNER_PID = 1

# Process
MAX_PATH = 260
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

# Error
NO_ERROR = 0

# Debug
PRINT_PAYLOAD = True

# Config
CONFIG=Config()
CFG_PARAM=CONFIG.params.getProperty("pcap")
API_URL=CONFIG.params.getProperty("pcap")["api_url"]
API=FenrisApi()
NOW=datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
FILENAME=NOW + ".pcap"

####################################################################################################################################
# Data headers/structures used to develop Management Information Base (MIB)
####################################################################################################################################
class MIB_TCPROW_OWNER_PID(Structure):
    """ Structure which contains information about IPv4 TCP connections and adresses, ports used and specific process ID (PID). """
    _fields_ = [
        ("dwState",      DWORD),
        ("dwLocalAddr",  DWORD),
        ("dwLocalPort",  DWORD),
        ("dwRemoteAddr", DWORD),
        ("dwRemotePort", DWORD),
        ("dwOwningPid",  DWORD)
    ]

class MIB_TCPTABLE_OWNER_PID(Structure):
    """ Structure which contains a table of process IDs (PIDs) and IPv4 TCP links, which is context bound to PIDs. """
    _fields_ = [
        ("dwNumEntries", DWORD),
        ("table",        MIB_TCPROW_OWNER_PID * 512)
    ]

class MIB_UDPROW_OWNER_PID(Structure):
    """ Structure that contains an entry from UDP listener table for IPv4 on the local computer.
    The entry also includes process ID (PID) used to call the bind function for the UDP endpoint."""
    _fields_ = [
        ("dwLocalAddr", DWORD),
        ("dwLocalPort", DWORD),
        ("dwOwningPid", DWORD)
    ]

class MIB_UDPTABLE_OWNER_PID(Structure):
    """ Structure that contains a UDP listener table for IPv4 on the local computer.
    Table also contains process ID (PID) that issued the call to bind function for each UDP endpoint."""
    _fields_ = [
        ("dwNumEntries", DWORD),
        ("table",        MIB_UDPROW_OWNER_PID * 512)
    ]

####################################################################################################################################
# Pcap class
####################################################################################################################################
class Pcap:
    """ Base class for Pcap. 
    Class inheritance from MIB classes (_MIB_TCPROW_OWNER_PID, _MIB_TCPTABLE_OWNER_PID, _MIB_UDPROW_OWNER_PID, _MIB_UDPTABLE_OWNER_PID)
    """
    def __init__(self, filename = FILENAME):
        """ Instance constructor
        :params filename: default filename for output files (string)
        """
        self.pcap_filter = "ip and (inbound or outbound)"
        self.pcap_file = self._PydivertClass(FILENAME, sync=True)

    ####################################################################################################################################
    # Class extensions
    ####################################################################################################################################
    # Extend PcapWriter from Scapy
    class _PydivertClass(_PcapWriter):
        """ Pcap Writer extender from Scapy. """
        def write(self, packet):
            scapy_packet = _IP(bytes(packet.raw))
            super().write(scapy_packet)

    ####################################################################################################################################
    # Static methods
    ####################################################################################################################################
    # Get prototype associated with the packet
    @staticmethod
    def _getProto(packet):
        """ Detect which protocol is associated with the packet. """
        if packet.tcp:
            return 'tcp'
        elif packet.udp:
            return 'udp'
        elif packet.icmp:
            return 'icmp'
        else:
            return 'unk'

    # Get process name
    @staticmethod
    def _getProcessName(pid):
        """ Get the name of the executable file for the given process. """
        process_name = 'Unknown'

        if pid == 4:
            process_name = 'System'
        elif pid:
            handle_process = windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if handle_process:
                lpImageFileName = create_string_buffer(MAX_PATH)

                if windll.psapi.GetProcessImageFileNameA(handle_process, lpImageFileName, MAX_PATH) > 0:
                    process_name = os.path.basename(lpImageFileName.value).decode()
                else:
                    print('Error: Failed to call GetProcessImageFileNameA')

                windll.kernel32.CloseHandle(handle_process)
   
        return process_name

    ####################################################################################################################################
    # Pcap data retrival methods
    ####################################################################################################################################
    def _getExtendedProtoTable(self):
        """ Retrieve table containing list of TCP/UDP endpoints available."""

        # TCP
        if self.proto == 'tcp':
            dw_size = DWORD(sizeof(MIB_TCPROW_OWNER_PID) * 512 + 4)
            tcp_table = MIB_TCPTABLE_OWNER_PID()

            if windll.iphlpapi.GetExtendedTcpTable(byref(tcp_table), byref(dw_size), False, AF_INET, TCP_TABLE_OWNER_PID_ALL, 0) != NO_ERROR:
                print("Error: Failed to call GetExtendedTcpTable")
                return
            
            for item in tcp_table.table[:tcp_table.dwNumEntries]:
                yield item

        # UDP
        elif self.proto == 'udp':
            dw_size = DWORD(sizeof(MIB_UDPROW_OWNER_PID) * 512 + 4)
            udp_table = MIB_UDPTABLE_OWNER_PID()

            if windll.iphlpapi.GetExtendedUdpTable(byref(udp_table), byref(dw_size), False, AF_INET, UDP_TABLE_OWNER_PID, 0) != NO_ERROR:
                print(GetLastError())
                print('Error: Failed to call GetExtendedUdpTable')
                return

            for item in udp_table.table[:udp_table.dwNumEntries]:
                yield item

    def _getPID(self, src_port):
        """ Get process ID (PID) on an existing port. """

        # Loop through the TCP/UDP table
        for item in self._getExtendedProtoTable():
            local_port = ntohs(item.dwLocalPort)
#            local_addr = inet_ntoa(struct.pack('L', item.dwLocalAddr))

            # Check if the local port matches the source port and return the process ID
            if local_port == src_port:
                return item.dwOwningPid
        else:
            return None


    def _getPIDNameProto(self, packet):
        """ Get process ID based on ephemeral port. """

        # Set default values
        self.pid = 0
        self.process_name = None

        # Check if the protocol is TCP or UDP and if the source port and destionation port is set
        if (self.proto == 'tcp' or self.proto == 'udp') and packet.src_port and packet.dst_port:

            # Get the ephemeral port
            ephemeral_port = packet.src_port

            # Set the ephemeral port
            if packet.direction == pydivert.consts.Direction.INBOUND:
                ephemeral_port = packet.dst_port
            elif packet.direction == pydivert.consts.Direction.OUTBOUND:
                ephemeral_port = packet.src_port

            self.pid = self._getPID(ephemeral_port)
            if self.pid:
                self.process_name = self._getProcessName(self.pid)

    ####################################################################################################################################
    # Capture method
    ####################################################################################################################################
    def capturePcap(self):
        """ Capture Pcap. """

        # Create a Pcap list which 
        self.pcap_data = []

        with pydivert.WinDivert(self.pcap_filter, layer=pydivert.Layer.NETWORK) as wd:
            print("------------------------------------------------------------------------------------------------------")
            for packet in wd:
                if self._getProto(packet) == 'icmp':
                    continue # disregard ICMP packets

                # Write to pcap file and set PID name and prototype
                self.pcap_file.write(packet)
                self.proto = self._getProto(packet)
                self._getPIDNameProto(packet)

                # API
                if CFG_PARAM["api"]:
                    if packet.is_outbound == True and packet.is_inbound == False:
                        direction = 'out'
                    elif packet.is_outbound == False and packet.is_inbound == True:
                        direction = 'in'
                    else:
                        direction = 'unk'

                    # Build Pcap dictionary
                    now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                    packet_data = {
                        "direction": direction,
                        "dst_addr": packet.dst_addr,
                        "dst_port": packet.dst_port,
                        "src_addr": packet.src_addr,
                        "src_port": packet.src_port,
#                            "payload": packet.payload,
                        "protocol": self.proto,
                        "process_name": self.process_name,
                        "pid": self.pid,
                        "request_timestamp": now,
                    }
                    
#                    API.send(API_URL, packet_data)
                    self.pcap_data.append(packet_data)

                if CFG_PARAM["debug"]:
                    print(f"Process ID: {self.pid}")
                    print(f"Process Name: {self.process_name}")
                    print(f"Protocol: {self.proto}")
                    print(f"Source address: {packet.src_addr}:{packet.src_port}")
                    print(f"Destination address: {packet.dst_addr}:{packet.dst_port}")
                    print("PACKET OBJECT:\n", packet)
                    print("------------------------------------------------------------------------------------------------------")

                    if CFG_PARAM["print_payload"]:
                        if packet.payload:
                            print("PACKET PAYLOAD:\n", hexdump(packet.payload))
                    print("------------------------------------------------------------------------------------------------------")

                wd.send(packet, recalculate_checksum=True)
