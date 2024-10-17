# myserver.py

import socket
from .myroom import MyMatchMaker
from server_room_system import *

class MyServer(Server):

    #this function is called when the client is not in a room and the client sent a request
    def handle_response(self, protocol:str, data, sender:socket.socket, client_data:ClientData):
        if protocol == Protocol.Response.MESSAGE:
            self.message(sender, client_data, data)
        
    def message(self, conn:socket, client_data:ClientData, data):
        message = f"<ID:{client_data.ID}> {data}"

        self.broadcast_message(message)

if __name__ == "__main__":
    server = MyServer(MyMatchMaker())
    server.run('127.0.0.1', 1234)