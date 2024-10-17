#myroom.py

from socket import socket
from server_room_system import *

class MyRoom(Room):

    #this function is called when the clients is registered in a room and the client sent a request
    def handle_response(self, protocol: str, data, sender: socket, client_data: ClientData) -> None:
        if protocol == Protocol.Response.MESSAGE:
            self.message(sender, client_data, data)
        
    def message(self, conn:socket, client_data:ClientData, data):
        message = f"<ID:{client_data.ID}> {data}"

        self.broadcast_message(message)

class MyMatchMaker(MatchMaker):

    #this function should return the custom room you made
    def create_room(self, ruleset):
        return MyRoom(ruleset)