import select
import socket
import sys
import queue
import time
import re
import os

def processArgs():
    return sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]

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


def checkLen():
    if file_bytes >= 1024:
        return 1024
    else:
        return file_bytes

# def testfile(readfile):
#     if os.path.isfile(readfile):
#         stream = open(readfile, 'rb')
#         binary_content = stream.read()
#         return (binary_content)
#     else:
#         return(False)

def writeToFile(str):
    # outputfile.write(str)
    X =1 

    

# kill program
doneSending = False

'''

# check if file exists and get binary content 
file_content = testfile(readfile)
file_bytes = len(file_content)
file_string = file_content.decode()

# open outfile and get ready to write
outputfile = open(outputfile, 'a+')

# file_content is the content of the file, len(file_content) is the # of bytes
if file_content == False:
'''

# Create a TCP/IP socket
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # Bind the socket to the port
# server_address = (ipAddress, UdpPort)
# udp_sock.bind(server_address)



# Sockets from which we expect to read
inputs = [udp_sock]

# Sockets to which we expect to write
outputs = [udp_sock]

# recieve buffer
rcv_buf = queue.Queue()

timeout = 30

# send buffer
snd_buf = queue.Queue()

lastbyte = 0

length = 0

# max payload
payload = 1024
# init window size
maxWindow = 5120

# init state
state = 'closed'

# first packet



# time variable 
curtime = time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime())

byte = 1

maxbytes = []
x = 4
while x < 10000:
    value = 1024*x + 1
    maxbytes.append(value)
    x += 5

if state == 'closed':
        firstpayload = "GET /{name} HTTP/1.0\nConnection: keep-alive".format(name = inputFiles[0])
        synFormat = "SYN|DAT|ACK\nSequence: 0\nLength: {len}\n Acknowledgment: -1\n Window: {win}\n\n{pay}".format(win = bufferSize, pay = firstpayload, len = len(firstpayload))
        # put syn packet in send buffer
        snd_buf.put(synFormat)
        state = 'syn-sent'

while True:

    # Wait for at least one of the sockets to be
    # ready for processing
#    print('waiting for the next event', file=sys.stderr)
    readable, writable, exceptional = select.select(inputs,
                                                    outputs,
                                                    inputs,
                                                    timeout)


    if udp_sock in readable: # rec
        # get packet
        packet = udp_sock.recvfrom(2048)
        
        print(packet)

        packetContent = packet[0].decode()
        head, seq, tail = packet[0].partition(b'\n\n')
        # head = head.decode()
        head = head.decode()

        # tail = tail.decode()
        head = head.split('\n')
        # commands, sequence, length, ack, win = head[0], head[1], head[2], head[3], head[4]
        command = head[0]

        if command == 'SYN|ACK':
            print(head)
            # log
            log = "{time}: Receive; {cmd}; {seq}; {len}; {ack}; {win}".format(time = curtime, cmd = command, seq = head[1], len = head[2], ack = head[3], win = head[4])
            print(log)
            # change state is syn-sent 
            if state == 'syn-sent':
                state = 'connection'

            # if state == 'closed':
            #     udp_sock.close()
            #     sys.exit()
        # # parse packet
        # head, seq, tail = packet.partition(b'\n\n')
        # head = head.decode()
        # # append to recv buffer
        # rcv_buf.put(head)
        # # model it
        # head = head.split('\n')
        # # get command
        # command = head[0]

        

    if udp_sock in writable: # send
            while not snd_buf.empty():
                try:
                    message = snd_buf.get_nowait()
                    # # get message
                    # 
                    # # split message
                    messagelist = message.split('\n')
                    if messagelist[0] == 'SYN|DAT|ACK':
                    # # print log
                        log = "{time}: Send; {cmd}; {seq}; {len}; {ack}; {win}".format(time = curtime, cmd = messagelist[0], seq = messagelist[1], len = messagelist[2], ack = messagelist[3], win =  messagelist[4])
                        print(log)
                   
                    # # send message
                    udp_sock.sendto(message.encode(), ("10.10.1.100", 8888))
                    time.sleep(0.1)
                except snd_buf.empty():
                    continue

            if state == 'open'and doneSending == False:
                while(lastbyte < 5121 and doneSending == False):
            # check payload length
                    length = checkLen()
                    if length != 1024:
                        doneSending = True
  
                        
                    # change length:
                    file_bytes = file_bytes - 1024

                    payload = file_string[0:length]
                    
                    # init packet
                    dat = "DAT\nSequence: {num}\nLength: {len}\n\n{pay}".format(num = byte, len = length, pay = payload)
                    # dat = "DAT\nSequence: {num}\nLength: {len}\n\n".format(num = lastbyte, len = length)
                    file_string = file_string[length:]
                     # send to snd buffer
                    snd_buf.put(dat)
                    byte = length + byte
                    # print(byte)
                    lastbyte = lastbyte + length
                time.sleep(0.1)
'''
 # check and handle ack
        if command == 'ACK':
                # log
                log = "{time}: Receive; {cmd}; {seq}; {len}".format(time = curtime, cmd = command, seq = head[1], len = head[2])
                print(log)
                # change state is syn-sent 
                if state == 'syn-sent':
                    state = 'open'

                if state == 'closed':
                    udp_sock.close()
                    sys.exit()
                
        
        if state == 'send-fin':
            # find sequence num and inc by 1 
            number = head[2].split()
            number = int(number[-1])
            fin = "FIN\nSequence: {num}\nLength: 0\n\n".format(num = byte)
            # send to snd buffer
            snd_buf.put(fin)
            state = 'fin-sent'

        if command == 'DAT':
            # log
            log = "{time}: Receive; {cmd}; {seq}; {len}".format(time = curtime, cmd = command, seq = head[1], len = head[2])
            print(log)
            # get len
            len = head[2].split()
            len = int(len[-1])
            # get seq
            seq = head[1].split()
            seq = int(seq[-1])
            # write 
            writeToFile(tail.decode())
            if len < 1024:        
                # close output file 
                X = 1
                
            
    
            if seq in maxbytes or len != 1024 :
                # byte = lastbyte + byte
                # print(byte)
                lastbyte = 1
                # set ACK message
                ack = "ACK\nAcknowlegment: {end}\nWindow: {win}\n\n".format(end =  len + seq, win = maxWindow)
                # send to snd buffer
                snd_buf.put(ack)
                if doneSending == True and state == 'open':
                    state = 'send-fin'


        # check if its a SYN packet
        if command == 'FIN':
            # change state
            state = 'closed'
            # log
            log = "{time}: Receive; {cmd}; {seq}; {len}".format(time = curtime, cmd = command, seq = head[1], len = head[2])
            print(log)
            # get seq
            seq = head[1].split()
            seq = int(seq[-1]) + 1
            # set ACK message
            ack = "ACK\nAcknowlegment: {num}\nWindow: {win}\n\n".format(num =  seq, win = maxWindow)
            # send to snd buffer
            snd_buf.put(ack)
        
        # check if its a SYN packet
        if command == 'SYN':
            # change state
            state = 'syn-sent'
            # log
            log = "{time}: Receive; {cmd}; {seq}; {len}".format(time = curtime, cmd = command, seq = head[1], len = head[2])
            print(log)
            # find sequence num and inc by 1 
            lastbyte = int(head[2][-1:]) + 1
            # set ACK message
            ack = "ACK\nAcknowlegment: {num}\nWindow: {win}\n\n".format(num = lastbyte, win = window)
            # send to snd buffer
            snd_buf.put(ack)
'''
       
       

       
 
                    
