# Parts of code reproduced from: https://github.com/fireeye/flare-fakenet-ng/blob/master/fakenet/diverters/winutil.py
import ctypes
import os
import pydivert
import pydivert.consts
import socket
import struct
import time
from hexdump import hexdump
#import logging
from modules.config import Config

from scapy.utils import PcapWriter as _PcapWriter
from scapy.layers.inet import IP as _IP
from ctypes import *
from ctypes.wintypes import *
from socket import *

# Interrim variables
#NO_ERROR = 0
#PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
#AF_INET = 2
#TCP_TABLE_OWNER_PID_ALL = 5
#UDP_TABLE_OWNER_PID = 1
#MAX_PATH = 260
#PRINT_PAYLOAD = True

####################################################################################################################################
# Data headers/structures used to develop Management Information Base (MIB)
####################################################################################################################################
class _MIB_TCPROW_OWNER_PID(Structure):
    """ Structure which contains information about IPv4 TCP connections and adresses, ports used and specific process ID (PID). """
    _fields_ = [
        ("dwState",         DWORD),
        ("dwLocalAddr",     DWORD),
        ("dwLocalPort",     DWORD),
        ("dwRemoteAddr",    DWORD),
        ("dwRemotePort",    DWORD),
        ("dwOwningPid",     DWORD)
    ]

class _MIB_TCPTABLE_OWNER_PID(Structure):
    """ Structure which contains a table of process IDs (PIDs) and IPv4 TCP links, which is context bound to PIDs. """
    _fields_ = [
        ("dwNumEntries",    DWORD),
        ("table",           _MIB_TCPROW_OWNER_PID * 512)
    ]

class _MIB_UDPROW_OWNER_PID(Structure):
    """ Structure that contains an entry from UDP listener table for IPv4 on the local computer.
    The entry also includes process ID (PID) used to call the bind function for the UDP endpoint."""
    _fields = [
        ("dwLocalAddr",     DWORD),
        ("dwLocalPort",     DWORD),
        ("dwOwningPid",     DWORD)
    ]

class _MIB_UDPTABLE_OWNER_PID(Structure):
    """ Structure that contains a UDP listener table for IPv4 on the local computer.
    Table also contains process ID (PID) that issued the call to bind function for each UDP endpoint."""

    _fields_ = [
        ("dwNumEntries",    DWORD),
        ("table",           _MIB_UDPROW_OWNER_PID * 512)
    ]

####################################################################################################################################
# Pcap class
####################################################################################################################################
class Pcap(_MIB_TCPROW_OWNER_PID, _MIB_TCPTABLE_OWNER_PID, _MIB_UDPROW_OWNER_PID, _MIB_UDPTABLE_OWNER_PID):
    """ Base class for Pcap. 
    Class inheritance from MIB classes (_MIB_TCPROW_OWNER_PID, _MIB_TCPTABLE_OWNER_PID, _MIB_UDPROW_OWNER_PID, _MIB_UDPTABLE_OWNER_PID)
    """
    def __init__(self, filename = 'asdf'):
        """ Instance constructor
        :params filename: default filename for output files (string)
        """

        # Get config parameters
        # Create config instance
        config = Config()
        self.config = config.params.getProperty("pcap")
        self.pcap_filter = "ip and (inbound or outbound)" # TODO: FIX THIS
#        self.pcap_filter = self.config["pcap_filter"]

        # Start Pydivert class
        pcap_filename = filename + "." + self.config["pcap_file_ext"]
#        interrim_netflow_file_ext = ".log"
#        self.pcap_file = self._PydivertClass(filename + interrim_pcap_file_ext, sync=True)
        self.pcap_file = self._PydivertClass(pcap_filename, sync=True)
#        self.netflow_file = filename + interrim_netflow_file_ext

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
    def _getProcessName(pid, pqli, mp):
        """ Get the name of the executable file for the given process. """
        process_name = 'Unknown'

        if pid == 4:
            process_name = 'System'
        elif pid:
            handle_process = windll.kernel32.OpenProcess(pqli, False, pid)
            if handle_process:
                full_file_path_pointer = create_string_buffer(mp)

                if windll.psapi.GetProcessImageFileNameA(handle_process, full_file_path_pointer, mp) > 0:
                    process_name = os.path.basename(full_file_path_pointer.value)
                else:
                    print('Error: Failed to call GetProcessImageFileNameA')

                windll.kernel32.CloseHandle(handle_process)

        return process_name



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
    # Pcap data retrival methods
    ####################################################################################################################################
    def _getExtendedProtoTable(self):
        """ Retrieve table containing list of TCP/UDP endpoints available."""

        if self.proto == 'tcp':
            dw_size = DWORD(sizeof(_MIB_TCPROW_OWNER_PID) * 512 + 4)
            tcp_table = _MIB_TCPTABLE_OWNER_PID()

            if windll.iphlpapi.GetExtendedTcpTable(byref(tcp_table), byref(dw_size), False, self.config["af_inet"], self.config["tcp_table_owner_pid_all"], 0) != self.config["no_error"]:
                print("Error: Failed to call GetExtendedTcpTable")
                return
            
            for item in tcp_table.table[:tcp_table.dwNumEntries]:
                yield item

        elif self.proto == 'udp':

            dw_size = DWORD(sizeof(_MIB_UDPROW_OWNER_PID) * 512 + 4)
            udp_table = _MIB_UDPTABLE_OWNER_PID()

            if windll.iphlpapi.GetExtendedUdpTable(byref(udp_table), byref(dw_size), False, self.config["af_inet"], self.config["udp_table_owner_pid"], 0) != self.config["no_error"]:
                print("Error: Failed to call GetExtendedUdpTable")

            for item in udp_table.table[:udp_table.dwNumEntries]:
                yield item


    def _getPID(self, src_port):
        """ Get process ID (PID) on an existing port. """

        # Loop through the TCP/UDP table
        for item in self._getExtendedProtoTable():
            local_port = ntohs(item.dwLocalPort)
#            local_addr = inet_ntoa(struct.pack('L', item.dwLocalAddr))
            pid = item.dwOwningPid

            # Check if the local port matches the source port and return the process ID
            if local_port == src_port:
                return pid

        else:
            return None


    def _getPIDNameProto(self, packet):
        """ Get process ID based on ephemeral port. """

        # Set default values
        self.pid = 0
        self.process_name = ''

        # Check if the protocol is TCP or UDP and if the source port and destionation port is set
        if (self.proto == 'tcp' or self.proto == 'udp') and packet.src_port and packet.dst_port:
#        if (packet.tcp or packet.udp) and packet.src_port and packet.dst_port:

            # Get the ephemeral port
            ephemeral_port = packet.src_port

            # Set the ephemeral port
            if packet.direction == pydivert.consts.Direction.INBOUND:
                ephemeral_port = packet.dst_port
            elif packet.direction == pydivert.consts.Direction.OUTBOUND:
                ephemeral_port = packet.src_port

            self.pid = self._getPID(ephemeral_port)
#            self.proto = self._getProto(packet) # remove

#            self.pid = self._getPID(ephemeral_port)
#            self.proto = self._getProto(packet)

            if self.pid:
                self.process_name = self._getProcessName(self.pid, self.config["process_query_limited_information"], self.config["max_path"]).decode('utf-8')
#            if self.pid:
#                process_name = self._getProcessName(pid)

#        return self.pid, process_name, proto
#        return self.pid, process_name, self.proto


    ####################################################################################################################################
    # Capture method
    ####################################################################################################################################
    def capturePcap(self):
        """ Capture Pcap. """

        with pydivert.WinDivert(self.pcap_filter) as wd:
                print("------------------------------------------------------------------------------------------------------")
                for packet in wd:
                        self.pcap_file.write(packet)
                        self.proto = self._getProto(packet)
                        self._getPIDNameProto(packet)

                        print(f"Process ID: {self.pid}")
                        print(f"Process Name: {self.process_name}")
                        print(f"Protocol: {self.proto}")
                        print(f"Source address: {packet.src_addr}:{packet.src_port}")
                        print(f"Destination address: {packet.dst_addr}:{packet.dst_port}")

#                        print(f"[{self.pid}] [{self.process_name}] {self.proto} - {packet.src_addr}:{packet.src_port} -> {packet.dst_addr}:{packet.dst_port}")

                        if self.config["print_payload"]:
                            print("Packet payload:")
                            hexdump(packet.payload)

                        print("------------------------------------------------------------------------------------------------------")

                        wd.send(packet)