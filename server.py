'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util
import re

class Server:
    '''
    This is the main Server Class. You will to write Server code inside this class.
    '''
    def __init__(self, dest, port, window):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))
        self.window = window
        self.clients={}
        self.dict={'forward_file':4,'ERR_SERVER_FULL':1,'ERR_USERNAME_UNAVAILABLE':1,'YES':1,'response_list':3,'FORWARD':4,'ERR_UNKNOWN_MSG':2,'DISCONNECT':1}
    
    def dc(self,user,client_soc):
        print(f'diconnected: {user} sent unknown command')
        del self.clients[user]
        msg=util.make_message('DISCONNECT',self.dict['DISCONNECT'],'')
        packet=util.make_packet('data',0,msg)
        self.sock.sendto(packet.encode('utf-8'),client_soc)
        
        
    
    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it
        '''
        print("HOST IS UP !! ")

        while True:
            packet,client_soc=self.sock.recvfrom(util.CHUNK_SIZE)
            msg=packet.decode('utf-8').split('|')[2]
            command=list(msg.split(' '))[0]
            length=int(list(msg.split(' '))[1])
            username=''
            if command == 'join':
                user=msg.split()[2]
                username=user
                if len(self.clients) >= util.MAX_NUM_CLIENTS:
                    string="disconnected:server_full!!"
                    msg=util.make_message('ERR_SERVER_FULL',self.dict['ERR_SERVER_FULL'],string)
                    packet=util.make_packet('data',0,msg)
                    self.sock.sendto(packet.encode('utf-8'),client_soc)
            
                elif user in self.clients.keys():
                    string ="disconnected:username_unavailable!!"
                    msg=util.make_message('ERR_USERNAME_UNAVAILABLE',self.dict['ERR_USERNAME_UNAVAILABLE'],string)
                    packet=util.make_packet('data',0,msg)
                    self.sock.sendto(packet.encode('utf-8'),client_soc)
                else:
                    print(f"join: {user}")
                    self.clients[user]=client_soc[1] 
            if command == 'request_list':
                if length == 0:
                    lst=''
                    lst='$'.join(sorted(self.clients.keys()))
                    user=list(self.clients.keys())[list(self.clients.values()).index(client_soc[1])]
                    #lst.replace(user,'')
                    print(f'request_users_list: {user}')
                    string=f"{lst}"
                    msg=util.make_message('response_list',self.dict['response_list'],string)
                    packet=util.make_packet('data',0,msg)
                    self.sock.sendto(packet.encode('utf-8'),client_soc)
                else:
                    self.dc(user,client_soc)
            
            elif command == 'msg':  
                    msg=msg.replace('  ',' ')
                    if re.match('msg \d+ \d+ .*',msg):  
                        lst=msg.split(' ')
                        no=int(lst[2])
                        clients = lst[3:2 + no + 1]
                        msg=' '.join(lst[3+len(clients):])
                        msg=msg.replace('$',' ')
                        user=list(self.clients.keys())[list(self.clients.values()).index(client_soc[1])]
                        print(f'msg: {user}')
                        string = f'msg: {user}: {msg}'
                        msg=util.make_message('FORWARD',self.dict['FORWARD'],string)
                        packet=util.make_packet('data',0,msg)
                        for i in range(0,no):
                            if clients[i] in self.clients.keys():
                                self.sock.sendto(packet.encode('utf-8'),(client_soc[0],self.clients[clients[i]]))
                            else:
                                print(f"msg: {user} to non-existent user {clients[i]}")
                    else:
                        self.dc(user,client_soc)

            elif command=='disconnect':
                if length == 4:
                    user=list(self.clients.keys())[list(self.clients.values()).index(client_soc[1])]
                    del self.clients[user]
                    print(f'disconnected: {user}')
                else:
                    self.dc(user,client_soc)
            elif command == 'send_file':
                
                try:
                    user=list(self.clients.keys())[list(self.clients.values()).index(client_soc[1])]
                    lst=msg.split()
                    no=int(lst[2])
                    clients = lst[3:2 + no + 1]
                    lst2=lst[3+len(clients):]
                    file=lst2[0]
                    data=lst2[1]
                    print(f'file: {user}: {file}')
                    sys.stdout.flush()
                    string=f'{user} {file} {data}'
                    msg=util.make_message('forward_file',self.dict['forward_file'],string)
                    packet=util.make_packet('data',0,msg)
            
                    for i in range(0,no):
                        if clients[i] in self.clients.keys():
                            self.sock.sendto(packet.encode('utf-8'),(client_soc[0],self.clients[clients[i]]))
                        else:
                            print(f"file: {user} to non-existent user {clients[i]}")
                    
                except:
                    self.dc(user,client_soc)
                
                
                
                


                    
                

            
                
        
        


 
                        




        

        

        
         
        #raise NotImplementedError

# Do not change this part of code

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"
    WINDOW = 3

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW = a

    SERVER = Server(DEST, PORT,WINDOW)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
