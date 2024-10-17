import socket
from gameroom import GameMatchMaker
from server_room_system.src import *

class GameServer(Server):

    def handle_response(self, protocol:str, data, sender:socket.socket, client_data:ClientData):
        pass


if __name__ == "__main__":
    server = GameServer(GameMatchMaker())
    server.run('127.0.0.1', 1234)