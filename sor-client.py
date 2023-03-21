import select
import socket
import sys
import queue
import time
import re
import os

def processArgs():
    return sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

def getFileNames():
    inputFiles = []
    outputFiles = []
    for i in range(5, len(sys.argv), 2):
        inputFiles.append(sys.argv[i])
        outputFiles.append(sys.argv[i + 1])
    return inputFiles, outputFiles

# unload the parameters
ipAddress, UdpPort, bufferSize, payloadLength = processArgs()
# get all the files described in the command line
inputFiles, outputFiles = getFileNames()
