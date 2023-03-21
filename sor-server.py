import select
import socket
import sys
import queue
import time
import re
import os

def processArgs():
    return sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]

server_ip_address, server_udp_port, client_buffer_size, client_payload_length = processArgs()