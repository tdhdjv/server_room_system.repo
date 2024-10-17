from socket import socket
from server_room_system import *

class GameRoom(Room):
    def handle_response(self, protocol: str, data, sender: socket, client_data: ClientData) -> None:
        
        if protocol == Protocol.Response.MESSAGE:
            self.message(sender, client_data, data)
        
    def message(self, conn:socket.socket, client_data:ClientData, data):
        message = f"<ID:{client_data.ID}> {data}"

        self.broadcast_message(message)

class GameMatchMaker(MatchMaker):
    def create_room(self, ruleset):
        return GameRoom(ruleset)