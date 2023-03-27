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
    return sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]

server_ip_address, server_udp_port, client_buffer_size, client_payload_length = processArgs()

close = 0

def checkForFile(requestline):
    decode = requestline.split()
    filename = decode[1][1:]
    return (os.path.isfile(filename), filename)

# Create a TCP/IP socket
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('', int(server_udp_port))
udp_sock.bind(server_address)




# Listen for incoming connections
udp_sock.listen(5)

# Sockets from which we expect to read
inputs = [udp_sock]

# Sockets to which we expect to write
outputs = [udp_sock]

# Outgoing message queues (socket:Queue)
message_queues = {}

buffer = []

# request message
request_message = {}

requestLine = []
curtime = time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime())
ipandport = "{ip}:{port}".format(ip = sys.argv[1], port = server_udp_port)

timeout = 30

lastmessage = 'not empty'

while inputs:

    # Wait for at least one of the sockets to be
    # ready for processing
#    print('waiting for the next event', file=sys.stderr)
    readable, writable, exceptional = select.select(inputs,
                                                    outputs,
                                                    inputs,
                                                    timeout)

    # Handle inputs


    for s in readable:


        if s is udp_sock:
            # A "readable" socket is ready to accept a connection
            connection, client_address = s.accept()
      
            connection.setblocking(0)
            inputs.append(connection)
            # outputs.append(s)
            request_message[connection] = queue.Queue() # OR queue
            #new_request[s] = True
            #persistent_socket[connection] = True
            # Give the connection a queue for data
            # we want to send
            message_queues[connection] = queue.Queue()
            

        else:
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
                    


    # Handle outputs
    for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
                log = request_message[s].get_nowait()
            except queue.Empty:
            # No messages need to be sent so stop watching
                outputs.remove(s)
                if s not in inputs:
                    inputs.remove(s)
                    outputs.remove(s)
                    s.close()
                    del message_queues[s]
                    del request_message[s]
            else:
                close = True
                s.send(next_msg.encode())
                print(log)
                decoded = next_msg.split()
                # print(decoded)
                for msg in decoded:
                    if re.search(re.compile(r"keep-alive"), msg):
                        close = False
                if close == True:
                    inputs.remove(s)
                    outputs.remove(s)
                    if s not in inputs:
                        s.close()
                        del message_queues[s]
                        del request_message[s]
                    
                

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
