#!/usr/bin/env python3
# encoding: utf-8
#
# Copyright (c) 2029 Zhiming Huang
#
import select
import socket
import sys
import queue
import time
import re
import os

def processArgs():
    return sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])

server_ip_address, server_udp_port, client_buffer_size, client_payload_length = processArgs()

close = 0

def checkForFile(requestline):
    decode = requestline.split()
    filename = decode[1][1:]

    return (os.path.isfile(filename), filename)

def checkLen():
    if file_bytes >= client_payload_length:
        return client_payload_length
    else:
        return file_bytes

def testfile(readfile):
    if os.path.isfile(readfile):
        stream = open(readfile, 'rb')
        binary_content = stream.read()
        return (binary_content)
    else:
        return(False)
byte = 1

file_bytes = 0

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

# Bind the socket to the port
server_address = (server_ip_address, server_udp_port)
udp_sock.bind(server_address)


# Sockets from which we expect to read
inputs = [udp_sock]

# Sockets to which we expect to write
outputs = [udp_sock]

# Outgoing message queues (socket:Queue)
message_queues = {}

buffer = []


snd_buf = queue.Queue()
# request message
request_message = {}

requestLine = []
curtime = time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime())
ipandport = "{ip}:{port}".format(ip = sys.argv[1], port = server_udp_port)

timeout = 30

lastmessage = 'not empty'
lastbyte = 0
test = 0

otherport = 0
key = ''
state = 'Closed'
donesending = False
            
curSeq = 0

while inputs:

    # Wait for at least one of the sockets to be
    # ready for processing
#    print('waiting for the next event', file=sys.stderr)
    readable, writable, exceptional = select.select(inputs,
                                                    outputs,
                                                    inputs,
                                                    timeout)

    # Handle inputs


    # for s in readable:


    #     if s is udp_sock:
    #         # A "readable" socket is ready to accept a connection
    #         connection, client_address = s.accept()
      
    #         connection.setblocking(0)
    #         inputs.append(connection)
    #         # outputs.append(s)
    #         request_message[connection] = queue.Queue() # OR queue
    #         #new_request[s] = True
    #         #persistent_socket[connection] = True
    #         # Give the connection a queue for data
    #         # we want to send
    #         message_queues[connection] = queue.Queue()

    #     else:
    if udp_sock in readable:
            packet = udp_sock.recvfrom(2048)

            otherport = (packet[-1][1])
            otherip = (packet[-1][0])
            # print(packet)
            # if test == 0:
            #     test = 1
            #     newpacket = "yo brother" 
            # #     snd_buf.put(newpacket)
            packetContent = packet[0].decode()
            head, seq, tail = packet[0].partition(b'\n\n')
            # head = head.decode()
            head = head.decode()
            tail = tail.decode()
            head = head.split('\n')
            commands, sequence, length, ack, win = head[0], head[1], head[2], head[3], head[4]
            intlen = length.split(' ')
            intseq = sequence.split(' ')
            commands = commands.split('|')
            
            if client_buffer_size != 0:
                # check if commands contains SYN
                for command in commands:
                    if command == 'SYN':
                        # recieved syn, payload contains http request
                        messages = tail.split('\n')
                        overallAck = int(intlen[-1]) + 1
                        # print(length)
                        # print(sequence)
                        for curRequest in range(len(messages)):
                            # check if request is in correct GET.... format
                                if re.search(re.compile(r"GET /.* HTTP/1.0"), messages[curRequest]):
                                # if it is, check if next request is connection: alive
                                    if re.search(re.compile(r"connection:\s*Keep-alive", re.IGNORECASE), messages[curRequest+1]):
                                    # if connection: keep-alive, check if file exists 
                                    
                                        found, filename = checkForFile(messages[curRequest])
                                        if found: 
                                            HTMLfile = open(filename, 'r')
                                            ok = 'HTTP/1.0 200 OK\r\nConnection: keep-alive\r\n\r\n{content}'.format(content = HTMLfile.read())
                                            sm = 'HTTP/1.0 200 OK'
                                            log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                            print(log)

                                            # check if ACK is included:
                                            for command in commands:
                                                if command == 'ACK':
                                            # send back syn ack pack
                                                    ack = "SYN|ACK\nSequence: {seq}\nLength: 0\nAcknowlegment: 1\nWindow: {win}\n\n".format(seq = curSeq, win = client_buffer_size)
                                                    snd_buf.put(ack)
                                            
                                                    curSeq += 1
                                            for command in commands:
                                                if command == 'DAT':
                                                    key = 'DatAck'
                                                    fileContent = testfile(filename)
                                                    file_bytes = len(fileContent)
                                                    file_string = fileContent.decode()
                                    
                                                    # datAck = "DAT|ACK\nSequence: {seq}\nLength = {len}}\nAcknowlegment: 1\nWindow: {win}\n\n".format(seq = curSeq, win = client_buffer_size, len = file_bytes)
                                                    state = 'connection open'
                                                    
                                                    # snd_buf.put(datAck)
                                                    

                                        else:
                                #       # file not found
                                            not_found = 'HTTP/1.0 404 Not Found\r\nConnection: keep-alive\r\n\r\n'
                                        #   PRINT notfound MESSAGE TO CLIENT 
                                            # message_queues[s].put(not_found)
                                        #   BUT FOR NOW....
                                            sm = 'HTTP/1.0 404 Not Found'
                                            log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                            print(log)
        
                if head[0] == 'DAT|ACK':
                    print(int(intlen[-1]))
                    print(int(intseq[-1]))
                    overallAck = int(intlen[-1]) + int(intseq[-1])
                    messages = tail.split('\n')
                    for curRequest in range(len(messages)):
                            # check if request is in correct GET.... format
                                if re.search(re.compile(r"GET /.* HTTP/1.0"), messages[curRequest]):
                                # if it is, check if next request is connection: alive
                                    if re.search(re.compile(r"connection:\s*Keep-alive", re.IGNORECASE), messages[curRequest+1]):
                                    # if connection: keep-alive, check if file exists 
                                    
                                        found, filename = checkForFile(messages[curRequest])
                                        if found: 
                                            HTMLfile = open(filename, 'r')
                                            ok = 'HTTP/1.0 200 OK\r\nConnection: keep-alive\r\n\r\n{content}'.format(content = HTMLfile.read())
                                            sm = 'HTTP/1.0 200 OK'
                                            log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                            print(log)

                                            
                                            
                                            key = 'DatAck'
                                            fileContent = testfile(filename)
                                            file_bytes = len(fileContent)
                                            file_string = fileContent.decode()
                                    
                                                    # datAck = "DAT|ACK\nSequence: {seq}\nLength = {len}}\nAcknowlegment: 1\nWindow: {win}\n\n".format(seq = curSeq, win = client_buffer_size, len = file_bytes)
                                            state = 'connection open'
                                            doneSending = False
                                                    # snd_buf.put(datAck)
                                                    

                                        else:
                                #       # file not found
                                            not_found = 'HTTP/1.0 404 Not Found\r\nConnection: keep-alive\r\n\r\n'
                                        #   PRINT notfound MESSAGE TO CLIENT 
                                            # message_queues[s].put(not_found)
                                        #   BUT FOR NOW....
                                            sm = 'HTTP/1.0 404 Not Found'
                                            log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                            print(log)

                if head[0] == 'FIN|ACK':
                    ak = ack.split()
                    ak = ak[-1]
                    seq = sequence.split()
                    seq = int(seq[-1])

                    finack = "FIN|ACK\nSequence: {seq}\nLength: 0\nAcknowlegment: {ack}\nWindow: {win}\n\n".format(seq = ak, win = client_buffer_size, ack = seq+1)
                    snd_buf.put(finack)
            else:
                    rst = "RST\nSequence: 0\nLength: 0\nAcknowlegment: -1\nWindow: 1\n\n"
                    snd_buf.put(rst)
  
  

    # Handle outputs
    if udp_sock in writable:
            while not snd_buf.empty():
                    try:
                        # get message
                        message = snd_buf.get_nowait()
                        
                        udp_sock.sendto(message.encode(), (otherip, otherport))
                        time.sleep(0.1)
                    except snd_buf.empty():
                        continue
            if state == 'connection open'and doneSending == False:
                
                while(doneSending == False):

            # check payload length
                    length = checkLen()
                    if length != client_payload_length:
                        doneSending = True
                    
                        
                    # change length:
                    file_bytes = file_bytes - client_payload_length

                    payload = file_string[0:length]
                  
                    if key == 'DatAck':
                    # init packet
                        dat = "DAT|ACK\nSequence: {num}\nLength: {len}\nAcknowledgement: {ack}\nWindow: {win}\n\n{pay}".format(num = byte, len = length, pay = payload, ack = overallAck, win = client_buffer_size)
                    # dat = "DAT\nSequence: {num}\nLength: {len}\n\n".format(num = lastbyte, len = length)
                    file_string = file_string[length:]
                     # send to snd buffer
                    snd_buf.put(dat)
                    byte = length + byte
                    # print(byte)
                    lastbyte = lastbyte + length
                time.sleep(0.1)

            '''
            message1 =  s.recv(1024).decode()
            if message1:   
                if message1.count('\n') != 1:
                    messages = message1.split('\n')

                    for curRequest in range(len(messages)):
                        # check if request is in correct GET.... format
                            if re.search(re.compile(r"GET /.* HTTP/1.0"), messages[curRequest]):
                            # if it is, check if next request is connection: alive
                                if re.search(re.compile(r"connection:\s*Keep-alive", re.IGNORECASE), messages[curRequest+1]):
                                # if connection: keep-alive, check if file exists 
                                    found, filename = checkForFile(messages[curRequest])
                                    if found: 
                                        HTMLfile = open(filename, 'r')
                                        ok = 'HTTP/1.0 200 OK\r\nConnection: keep-alive\r\n\r\n{content}'.format(content = HTMLfile.read())
                                        sm = 'HTTP/1.0 200 OK'
                                        log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                        request_message[s].put(log)
                                    #   PRINT OK MESSAGE TO CLIENT 
                                        message_queues[s].put(ok)
                                    #   BUT FOR NOW....
                                        
                                    # output file contents 
                                        
                                    #   PRINT file contents TO CLIENT 
                                    #   message_queues[connection].put(HTMLfile.read())
                                    #   BUT for now....
                                        

                                    else:
                            #       # file not found
                                        not_found = 'HTTP/1.0 404 Not Found\r\nConnection: keep-alive\r\n\r\n'
                                    #   PRINT notfound MESSAGE TO CLIENT 
                                        message_queues[s].put(not_found)
                                    #   BUT FOR NOW....
                                        sm = 'HTTP/1.0 404 Not Found'
                                        log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                        request_message[s].put(log)
                                else:
                                # check for bad header line
                                    if not re.search(re.compile(r"connection:\s*close", re.IGNORECASE), messages[curRequest+1]) and messages[curRequest + 1] != '':
                                    # if we are here, the header line is bad
                                        bad_request = 'HTTP/1.0 400 Bad Request\r\n\r\n'
                                    #   PRINT notfound MESSAGE TO CLIENT 
                                        message_queues[s].put(bad_request)
                                        sm = 'HTTP/1.0 400 Bad Request'
                                        log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                        request_message[s].put(log)
                                    #   BUT FOR NOW....
                                    found, filename = checkForFile(messages[curRequest])
                                    if found: 
                                        HTMLfile = open(filename, 'r')
                                        ok = 'HTTP/1.0 200 OK\r\nConnection: close\r\n\r\n{content}'.format(content = HTMLfile.read())
                                    #   PRINT OK MESSAGE TO CLIENT 
                                        message_queues[s].put(ok)
                                    #   BUT FOR NOW....
                                        sm = 'HTTP/1.0 200 OK'
                                        log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                        request_message[s].put(log)
                                    # output file contents 
                                        
                                    #   PRINT file contents TO CLIENT \c
          


                                    else:
                                       # file not found
                                        not_found = 'HTTP/1.0 404 Not Found\r\nConnection: close\r\n\r\n'
                                        #   PRINT notfound MESSAGE TO CLIENT 
                                        message_queues[s].put(not_found)
                                        sm = 'HTTP/1.0 404 Not Found'
                                        log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                        request_message[s].put(log)
                                        #   BUT FOR NOW....
                                        
            
                                        # CLOSE CONNECTION

                            # if connection: closed, check if file exists 
                                    found, filename = checkForFile(messages[curRequest])
                                    if found: 
                                        HTMLfile = open(filename, 'r')
                                        ok = 'HTTP/1.0 200 OK\r\n\r\n{content}'.format(content = HTMLfile.read())
                                    #   PRINT OK MESSAGE TO CLIENT 
                                        message_queues[s].put(ok)
                                        sm = 'HTTP/1.0 200 OK'
                                        log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                        request_message[s].put(log)

                                    # check if end of requests: \n\n
                            elif messages[curRequest] == '':
                                    # empty line detected
                                if curRequest + 1 < len(messages):
                                    # check if it's last line
                                    if messages[curRequest + 1] == '':
                                    # if we are here, last two lines are empty
                                        x = 1 


                    
                    # BAD REQUEST  
                            else:
        # ensure it's not the header
                                if not re.search(re.compile(r"connection:\s*Keep-alive", re.IGNORECASE), messages[curRequest]) and not re.search(re.compile(r"connection:\s*close", re.IGNORECASE), messages[curRequest]) and messages[curRequest] != '':
                                    bad_request = 'HTTP/1.0 400 Bad Request\r\n\r\n'
                                    sm = 'HTTP/1.0 400 Bad Request'
                                    log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = messages[curRequest], res = sm)
                                    request_message[s].put(log)
            #   PRINT notfound MESSAGE TO CLIENT 
                                    message_queues[s].put(bad_request)
            #   BUT FOR NOW....

                    if s not in outputs:
                        outputs.append(s)
                                        



                else:
                    # check if message is empty
                    if not re.search(re.compile(r"connection:\s*Keep-alive", re.IGNORECASE), message1) and not re.search(re.compile(r"connection:\s*close", re.IGNORECASE), message1) and not re.search(re.compile(r"GET /.* HTTP/1.0"), message1) and message1 != '\n':
                        bad_request = 'HTTP/1.0 400 Bad Request\r\n\r\n'
            #   PRINT notfound MESSAGE TO CLIENT 
                        message_queues[s].put(bad_request)
                        sm = 'HTTP/1.0 400 Bad Request'
                        log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = message1[:-1], res = sm)
                        request_message[s].put(log)
                        if s not in outputs:
                            outputs.append(s)

                    if lastmessage == '\n':
                        if message1 == '\n':
                            x = 1 
                            
                    if re.search(re.compile(r"GET /.* HTTP/1.0"), message1):
                        buffer.append(message1)

                    if re.search(re.compile(r"connection:\s*Keep-alive", re.IGNORECASE), message1):
                        buffer.append(message1)

                    
                    if message1 == '\n':
                        
                        # time to process
                        for line in range(len(buffer)):
                            # check if first line is GET
                            if re.search(re.compile(r"GET /.* HTTP/1.0"), buffer[line]):
                                # if it is: check it has connection keep alive or not
                                if line + 1 >= len(buffer):
                                    # if this is the only line:
                                    # check then close
                                    
                                    found, filename = checkForFile(buffer[line])
                    
                                    if not found:
                                        not_found = 'HTTP/1.0 404 Not Found\r\nConnection: close\r\n\r\n'
                                            #   PRINT notfound MESSAGE TO CLIENT 
                                        message_queues[s].put(not_found)
                                        sm = 'HTTP/1.0 404 Not Found'
                                        log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = buffer[line][:-1], res = sm)
                                        request_message[s].put(log)
                                            
                                    else:
                                        # found file and close
                                        HTMLfile = open(filename, 'r')
                                        ok = 'HTTP/1.0 200 OK\r\nConnection: close\r\n\r\n{content}'.format(content = HTMLfile.read())
                                        sm = 'HTTP/1.0 200 OK'
                                        log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = buffer[line][:-1], res = sm)
                                        request_message[s].put(log)
                                        message_queues[s].put(ok)
                                else:
                                    # have more lines: 
                                        # check if keep alive
                                        if re.search(re.compile(r"connection:\s*Keep-alive", re.IGNORECASE), buffer[line+1]):

                                            found, filename = checkForFile(buffer[line])
            
                                            if not found:
                                            # process and not close
                                                not_found = 'HTTP/1.0 404 Not Found\r\nConnection: keep-alive\r\n\r\n'
                                                #   PRINT notfound MESSAGE TO CLIENT 
                                                message_queues[s].put(not_found)
                                                sm = 'HTTP/1.0 404 Not Found'
                                                log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = buffer[line][:-1], res = sm)
                                                request_message[s].put(log)
                                                
                                            else:
                                            # found file and keep alive
                                                HTMLfile = open(filename, 'r')
                                                ok = 'HTTP/1.0 200 OK\r\nConnection: keep-alive\r\n\r\n{content}'.format(content = HTMLfile.read())
                                                message_queues[s].put(ok)
                                                sm = 'HTTP/1.0 200 OK'
                                                log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = buffer[line][:-1], res = sm)
                                                request_message[s].put(log)

                                                
                                        else:

                                            found, filename = checkForFile(buffer[line])
                        
                                            if not found:
                                                not_found = 'HTTP/1.0 404 Not Found\r\nConnection: close\r\n\r\n'
                                                #   PRINT notfound MESSAGE TO CLIENT 
                                                message_queues[s].put(not_found)
                                                sm = 'HTTP/1.0 404 Not Found'
                                                log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = buffer[line][:-1], res = sm)
                                                request_message[s].put(log)
                                                
                                            else:
                                            # found file and close
                                                HTMLfile = open(filename, 'r')
                                                ok = 'HTTP/1.0 200 OK\r\nConnection: close\r\n\r\n{content}'.format(content = HTMLfile.read())
                                                message_queues[s].put(ok)
                                                sm = 'HTTP/1.0 200 OK'
                                                log = "{time}: {ipport} {req}; {res}".format(time = curtime, ipport = ipandport, req = buffer[line][:-1], res = sm)
                                                request_message[s].put(log)
                                        
                                   #  process and close

                        # clear buffer
                        buffer = []

                  

                    lastmessage = message1
                    if s not in outputs:
                        outputs.append(s)
            '''
            
                    



            # try:
            #     next_msg = message_queues[s].get_nowait()
            #     log = request_message[s].get_nowait()
            # except queue.Empty:
            # # No messages need to be sent so stop watching
            #     outputs.remove(s)
            #     if s not in inputs:
            #         inputs.remove(s)
            #         outputs.remove(s)
            #         s.close()
            #         del message_queues[s]
            #         del request_message[s]
            # else:
            #     close = True
            #     s.send(next_msg.encode())
            #     print(log)
            #     decoded = next_msg.split()
            #     # print(decoded)
            #     for msg in decoded:
            #         if re.search(re.compile(r"keep-alive"), msg):
            #             close = False
            #     if close == True:
            #         inputs.remove(s)
            #         outputs.remove(s)
            #         if s not in inputs:
            #             s.close()
            #             del message_queues[s]
            #             del request_message[s]
                    
                

    # Handle "exceptional conditions"
    for s in exceptional:
        #print('exception condition on', s.getpeername(),
         #     file=sys.stderr)
        # Stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        # Remove message queue
        del message_queues[s]
    
    # if s not in readable and writable and exceptional:
    #      #handle timeout events
    #      socket.settimeout(30)
