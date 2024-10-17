'''
Server class is in charge of:
1. accepting clients 
2. sending data to clients
3. recieving data from clients
4. handling rooms
'''

import socket
import selectors
from ..utils import data_handler
from threading import Thread

from .protocols import Protocol

from .client import ClientData
from .room import Room, Match_Maker

class Server:

    running = True
    close_when_empty = False
    id = 0
    clients_room:dict[socket.socket, Room] = {}
    rooms:list = []

    def __init__(self, match_maker:Match_Maker) -> None:
        self.match_maker = match_maker

    def run(self, host:str, port:int) -> None:
        #initialize socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Connected to {host}: {port}")
        server.bind((host, port))
        server.setblocking(False)
        server.listen()
        
        #intialize selectors
        self.sel = selectors.DefaultSelector()
        self.sel.register(server, selectors.EVENT_READ, data = None)

        #create thread for commands such as kick, close
        command_thread = Thread(target=self.commands, daemon=True)
        command_thread.start()

        #loop
        while self.running:
            events = self.sel.select(timeout=1)
            for key, _ in events:
                data = key.data
                sock = key.fileobj

                #if the data is none it means it is the server socket
                if data == None:
                    self.accept(sock)
                else:
                    self.handle_client(sock, data)
        
        server.close()

    def commands(self):
        while self.running:
            command = input()
            if command == 'close':
                self.close()
    
    def close(self):
        if len(self.clients_room.keys()) <= 0:
            self.running = False
        for client in self.clients_room.keys():
            client.send(data_handler.encode(Protocol.Response.COMMAND, 'close'))
        self.close_when_empty = True

    def accept(self, server:socket.socket):
        conn, addr = server.accept()
        print(f"Connected to {addr}")
        client_data = ClientData(self.id, addr)
        self.id += 1

        #send the client data to the client
        conn.send(data_handler.encode(Protocol.Response.CLIENT_DATA, client_data))

        #registering
        self.clients_room[conn] = None
        self.sel.register(conn, selectors.EVENT_READ, data = client_data)

    def handle_client(self, conn:socket.socket, client_data:ClientData):
        request = conn.recv(1024)

        if request:
            room:Room = self.clients_room[conn]

            packet = data_handler.decode(request)
            protocol = packet['protocol']
            data = packet['data']
            
            #pre built responses
            if protocol == Protocol.Request.ROOM_RULSET:
                self.enter(conn, client_data, data)
            if protocol == Protocol.Request.COMMAND:
                self.enter(conn, client_data, data)
            
            #this is for other protocols
            if room:
                room.handle_response(protocol, data, conn, client_data)
                
        else:
            #if the request is none that means the client has left
            self.kick_client(conn, client_data)

    def kick_client(self, conn:socket.socket, client_data:ClientData):
        self.sel.unregister(conn)
        print(f"{client_data.ADDRESS} has Disconnected!")

        #closing room logic
        room = self.clients_room.pop(conn)
        if room:
            room.remove_client(conn)
            if not room.has_min_client() and not self.close_when_empty:
                room.close()
                print('Closing Room!')
        
        #closing server logic
        if self.close_when_empty and len(self.clients_room.keys()) <= 0:
            self.running = False
    
    def enter(self, conn:socket.socket, client_data:ClientData, data):
        #match making
        ruleset = data
        ready_room = self.match_maker.add_client(conn, client_data, ruleset)
        if ready_room:
            print('Room Ready!')
            self.rooms.append(ready_room)
            for client in ready_room.active_clients.keys():
                self.clients_room[client] = ready_room

    def command(self, conn:socket.socket, client_data:ClientData, data):
        if data == 'quit':
            self.send_command(conn, 'close')
    
    def send_message(self, conn:socket.socket, text:str):
        conn.send(data_handler.encode(Protocol.Response.MESSAGE, text))

    def send_command(self, conn:socket.socket, command:str):
        conn.send(data_handler.encode(Protocol.Response.COMMAND, command))

    def send(self, protocol:str, conn:socket.socket, data):
        conn.send(data_handler.encode(protocol, data))

    def broadcast(self, protocol, data) -> None:
        packet = data_handler.encode(protocol, data)
        for client in self.clients_room.keys():
            client.send(packet)
        
    def broadcast_message(self, text:str) -> None:
        packet = data_handler.encode(Protocol.Response.MESSAGE, text)
        for client in self.clients_room.keys():
            client.send(packet)

    def broadcast_command(self, command:str) -> None:
        packet = data_handler.encode(Protocol.Response.COMMAND, command)
        for client in self.clients_room.keys():
            client.send(packet)

    def handle_response(self, protocol:str, data, sender:socket.socket, client_data:ClientData):
        '''
        This function is called when the client is not in a room and a client sent a request
        The Implementation is up to the subclasses
        '''
        pass

if __name__ == "__main__":
    server = Server()
    server.run('127.0.0.1', 1234)
