from pickle import FALSE, TRUE
import select
import socket
import sys
import queue
import time
import re
import os

def processArgs():
    return sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])

def getFileNames():
    for i in range(5, len(sys.argv), 2):
        inputFiles.append(sys.argv[i])
        outputFiles.append(sys.argv[i + 1])


# unload the parameters
ipAddress, UdpPort, bufferSize, payloadLength = processArgs()
# get all the files described in the command line
inputFiles = []
print(inputFiles)
outputFiles = []
getFileNames()
numFiles = len(inputFiles)



# def testfile(readfile):
#     if os.path.isfile(readfile):
#         stream = open(readfile, 'rb')
#         binary_content = stream.read()
#         return (binary_content)
#     else:
#         return(False)

def writeToFile(str):
    outputfile.write(str)

def createOutFile(currentFile):
    outputfile = open(outputFiles[currentFile], 'a+')   
    return outputfile

def sendNexthttp(currentFile, seq, ack):
    httpreq = "GET /{name} HTTP/1.0\nConnection: keep-alive".format(name = inputFiles[currentFile])
    rdpreq = "DAT|ACK\nSequence: {seqs}\nLength: {leng}\n Acknowledgment: {ak}\n Window: {win}\n\n{pay}".format(ak = ack, seqs = seq, win = bufferSize, pay = httpreq, leng = len(httpreq))
        # put syn packet in send buffer

    snd_buf.put(rdpreq)

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

currentFile = 0

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
payload = payloadLength
# init window size
maxWindow = bufferSize
lasttemp = False

# init state
state = 'closed'
savedSeq = 0
savedLen = 0
# first packet
outputfile = createOutFile(currentFile)

lastfile = False
# time variable 
curtime = time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime())

byte = 1

maxbytes = []
x = 4
while x < 10000:
    value = payloadLength*x + 1
    maxbytes.append(value)
    x += 5

if state == 'closed':
        firstpayload = "GET /{name} HTTP/1.0\nConnection: keep-alive".format(name = inputFiles[0])
        synFormat = "SYN|DAT|ACK\nSequence: 0\nLength: {leng}\n Acknowledgment: -1\n Window: {win}\n\n{pay}".format(win = bufferSize, pay = firstpayload, leng = len(firstpayload))
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
        
        # print(packet)

        packetContent = packet[0].decode()
        head, seq, tail = packet[0].partition(b'\n\n')
        # head = head.decode()
        head = head.decode()

        # tail = tail.decode()
        head = head.split('\n')
        # commands, sequence, length, ack, win = head[0], head[1], head[2], head[3], head[4]
        command = head[0]
        if command == 'RST':
            log = "{time}: Receive; {cmd}; {seq}; {leng}; {ack}; {win}".format(time = curtime, cmd = command, seq = head[1], leng = head[2], ack = head[3], win = head[4])
            print(log)
            sys.exit()

        if command == 'SYN|ACK':
            # print(head[2])
            # log
            # leng1 = head[2].split()
            # leng1 = int(leng1[-1])
            log = "{time}: Receive; {cmd}; {seq}; {leng}; {ack}; {win}".format(time = curtime, cmd = command, seq = head[1], leng = head[2], ack = head[3], win = head[4])
            print(log)
            # change state is syn-sent 
            if state == 'syn-sent':
                state = 'connection'
        
        if command == 'FIN|ACK':
            log = "{time}: Receive; {cmd}; {seq}; {leng}; {ack}; {win}".format(time = curtime, cmd = command, seq = head[1], leng = head[2], ack = head[3], win = head[4])
            print(log)
            seqq = head[3].split()
            seqq = seqq[-1]
            ak = head[1].split()
            ak = int(ak[-1])
            ack = "ACK\nSequence: {ackseq}\nLength: 0\nAcknowlegment: {end}\nWindow: {win}\n\n".format(ackseq =  seqq, win = maxWindow, end = ak+1)
            snd_buf.put(ack)
            sys.exit()

        if command == 'DAT|ACK':

            log = "{time}: Receive; {cmd}; {seq}; {leng}; {ack}; {win}".format(time = curtime, cmd = command, seq = head[1], leng = head[2], ack = head[3], win = head[4])
            print(log)
            # get len
            leng = head[2].split()
            leng = int(leng[-1])

            # get seq
            seq = head[1].split()
            seq = int(seq[-1])
            # write 
            writeToFile(tail.decode())

            if leng < payloadLength:        
                # print(lastfile)
                # close output file 
                if lastfile == True:
                    lasttemp = True
                    # state = 'fin-sent'
                    finAck = "FIN|ACK\nSequence: {ackseq}\nLength: 0\nAcknowlegment: {end}\nWindow: {win}\n\n".format(ackseq =  savedSeq + savedLen, win = maxWindow, end = leng + seq)
                    # send to snd buffer
                    snd_buf.put(finAck)
                else:

                    outputfile.close()
                    if numFiles != 1:
                        maxbytes = []
                        x = 4
                        while x < 10000:
                            value = payloadLength*x + (leng + 1)
                            maxbytes.append(value)
                            x += 5
    
                        
                        # currentFile = currentFile + 1
                        # if currentFile == numFiles:
                        #     lastfile = True
                        # outputfile = createOutFile(currentFile)
                        # aklen = head[3].split()
                        # aklen = int(aklen[-1]) 
                        # sendNexthttp(currentFile, aklen, leng + 1)

                        if currentFile != numFiles -1 :
                            currentFile = currentFile + 1

                            if currentFile == numFiles -1 :
                                lastfile = True
                            outputfile = createOutFile(currentFile)
                            aklen = head[3].split()
                            aklen = int(aklen[-1]) 
                            sendNexthttp(currentFile, aklen, leng + 1)
            

            
            if seq in maxbytes and lasttemp == False:
                # byte = lastbyte + byte
                # if doneSending == False:
                if state == 'fin-sent':
             
                    # print('here')
                    finAck = "FIN|ACK\nSequence: {ackseq}\nLength: 0\nAcknowlegment: {end}\nWindow: {win}\n\n".format(ackseq =  savedSeq + savedLen, win = maxWindow, end = leng + seq)
                    # send to snd buffer
                    snd_buf.put(finAck)
                else:
   
                    
                    ack = "ACK\nSequence: {ackseq}\nLength: 0\nAcknowlegment: {end}\nWindow: {win}\n\n".format(ackseq =  savedSeq + savedLen, win = maxWindow, end = leng + seq)
                    # send to snd buffer
                    snd_buf.put(ack)
                # lastbyte = 1
                # set ACK message
                # ack = "DAT|ACK\nSequence: {ackseq}\nAcknowlegment: {end}\nWindow: {win}\n\n".format(end =  len + seq, win = maxWindow, ackseq = head[3])
                # send to snd buffer
                # snd_buf.put(ack)
                if doneSending == True and state == 'open':
                    state = 'send-fin'

        

    if udp_sock in writable: # send
            while not snd_buf.empty():
                try:
                    message = snd_buf.get_nowait()
                    
                    
                    # # get message
                    # 
                    # # split message
                    messagelist = message.split('\n')
                    if messagelist[0] == 'SYN|DAT|ACK' or messagelist[0] == 'DAT|ACK' or messagelist[0] == 'FIN|ACK':
                    # # print log
                        log = "{time}: Send; {cmd}; {seq}; {leng}; {ack}; {win}".format(time = curtime, cmd = messagelist[0], seq = messagelist[1], leng = messagelist[2], ack = messagelist[3], win =  messagelist[4])
                        print(log)
                        if messagelist[0] == 'DAT|ACK':
                            savedSeq = messagelist[1].split()
                            savedSeq = int(savedSeq[-1])
                            savedLen = messagelist[2].split()
                            savedLen = int(savedLen[-1])
                    if messagelist[0] == 'ACK':
                    # # # print log
                        # print("here")
                        log = "{time}: Send; {cmd}; {seq}; {leng}; {ack}; {win}".format(time = curtime, cmd = messagelist[0], seq = messagelist[1], leng = messagelist[2], ack = messagelist[3], win =  messagelist[4])
                        print(log)
                    # # send message
                    udp_sock.sendto(message.encode(), ("10.10.1.100", 8888))
                    time.sleep(0.1)
                except snd_buf.empty():
                    continue

   
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
       
       

       
 
                    
