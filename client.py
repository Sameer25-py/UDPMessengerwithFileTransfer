'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import util
import time
import select
import re

'''
Write your code inside this class. 
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen 
for incoming messages in this function.
'''
def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")


class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port, window_size):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username
        self.window = window_size
        self.dict={'disconnect':1,'join':1,'request_list':2,'msg':3,'send_file':4}

    

    def start(self):
        '''
        Main Loop is here
        Start by sending the server a JOIN message.
        Waits for userinput and then process it
        '''
        #Join
        
        string = f"{self.name}"
        msg=util.make_message('join',self.dict['join'],string)
        packet=util.make_packet('data',0,msg)
        self.sock.sendto(packet.encode('utf-8'),(self.server_addr,self.server_port))
        while True:
            inp=str(input(''))  
            if 'quit' == inp:
                s='quitting'
                print(s)
                sys.stdout.flush()
                inp = str(inp.replace('msg',''))
                msg=util.make_message('disconnect',self.dict['disconnect'],inp)
                packet=util.make_packet('data',0,msg)
                self.sock.sendto(packet.encode('utf-8'),(self.server_addr,self.server_port))
                self.sock.close()
                os._exit(1)
            
            elif 'list'==inp:
                inp=inp.replace('list','')
                msg=util.make_message('request_list',self.dict['request_list'],inp)
                packet=util.make_packet('data',0,msg)
                self.sock.sendto(packet.encode('utf-8'),(self.server_addr,self.server_port))
            elif 'msg' in inp:
                inp=inp.replace('msg','')
                msg=util.make_message('msg',self.dict['msg'],inp)
                
                packet=util.make_packet('data',0,msg)
                
                self.sock.sendto(packet.encode('utf-8'),(self.server_addr,self.server_port))

            elif 'file' in inp:
                
                file=inp.split(' ')[-1]
                
                try:
                    with open(file,'r') as f:
                        data=f.read()
                except:
                    print('file not found')
                    pass
                data=data.replace(' ','[s]').replace('\n','[nl]')
                string =" ".join(inp.split()[1:])
                string=string + ' ' + data
                msg=util.make_message('send_file',self.dict['send_file'],string)
                packet=util.make_packet('data',0,msg)
                self.sock.sendto(packet.encode('utf-8'),(self.server_addr,self.server_port))
                
            else:
                print(f'incorrect userinput format')
                
        
                
                

                
            
                              
                            
    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        
        '''
        while True:
    
            packet=self.sock.recv(util.CHUNK_SIZE)
            packet=packet.decode('utf-8')
            message=util.parse_packet(packet)[2]
            msg=message.split(' ')
            
            if 'ERR_SERVER_FULL' in msg[0]:
                print(msg[2])
                self.sock.close()
                os._exit(1)
            elif 'ERR_USERNAME_UNAVAILABLE' in msg[0]:
                print(msg[2])  
                self.sock.close()
                os._exit(1)
            
            elif 'response_list' in msg[0]:
                msg1=msg[2].replace('$'," ")
                print(f"list: {msg1}")
                
            elif 'FORWARD' in msg[0]:
                msg1=' '.join(msg[2:])
                msg1=msg1.replace('  ',' ')
                print(msg1)
                
            
            elif 'DISCONNECT' in msg[0]:
                print('disconnected: server received a unknown command')
                self.sock.close()
                os._exit(1)
            
            elif 'forward_file' in msg[0]:
                
                client = msg[2]
                file=msg[3]
                data=msg[4].replace('[s]',' ').replace('[nl]','\n')
                with open(f'{client}_{file}','w+') as f:
                    f.write(data)
                    f.close()
                print(f'file: {client}: {file}')
                



   
                           

            
            
                



        #raise NotImplementedError



# Do not change this part of code
if __name__ == "__main__":
    
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    WINDOW_SIZE = 3
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW_SIZE = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT, WINDOW_SIZE)
    
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
        #T.join()         
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
