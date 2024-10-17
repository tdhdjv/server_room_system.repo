'''
Room class is in charge of:
1. provides an isolated environment
2. handles/sends data to the client in this room (and NO ONE ELSE)
'''

import socket
from .client import Client_Data
from ..utils import data_handler
from .protocols import Protocol
from dataclasses import dataclass

@dataclass
class RuleSet:
    CLIENT_COUNT:int

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RuleSet):
            return False
        return value.CLIENT_COUNT == self.CLIENT_COUNT
    
    def __hash__(self) -> int:
        return self.CLIENT_COUNT.__hash__()

class Room:

    MIN_CLIENT_COUNT = 2
    rule_set:RuleSet
    active_clients:dict[socket.socket]

    def __init__(self, ruleset) -> None:
        self.rule_set = ruleset
        self.active_clients = {}

    def ready(self):
        self.broadcast_command('room ready!')

    def handle_response(self, protocol:str, data, sender:socket.socket, client_data:Client_Data) -> None:
        '''
        This function is called when a client is a room and the sent a request The implementation is up the subclass
        '''
        pass

    def add_client(self, client:socket.socket, client_data):
        self.active_clients[client] = client_data

    def remove_client(self, client:socket.socket):
        self.active_clients.pop(client)

    def broadcast(self, protocol, data) -> None:
        packet = data_handler.encode(protocol, data)
        for client in self.active_clients.keys():
            client.send(packet)
        
    def broadcast_message(self, text:str) -> None:
        packet = data_handler.encode(Protocol.Response.MESSAGE, text)
        for client in self.active_clients.keys():
            client.send(packet)

    def broadcast_command(self, command:str) -> None:
        packet = data_handler.encode(Protocol.Response.COMMAND, command)
        for client in self.active_clients.keys():
            client.send(packet)
    
    def has_min_client(self):
        return len(self.active_clients) >= self.MIN_CLIENT_COUNT
    
    def close(self):
        for client in self.active_clients.keys():
            client.send(data_handler.encode(Protocol.Response.COMMAND, 'close'))

'''
Math_Maker is in charge or
1. putting client into the appropriate rooms
'''

class MatchMaker:
    non_ready_rooms:dict[RuleSet, Room] = {}

    def add_client(self, client:socket.socket, client_data:Client_Data, ruleset:RuleSet) -> Room:
        "The return value tells you the rooms that are ready"
        #if there is a room with the same ruleset add the client to that room
        room = self.non_ready_rooms.get(ruleset)
        if room:
            room.add_client(client, client_data)
            #check if the room is ready
            if len(room.active_clients) >= room.rule_set.CLIENT_COUNT:
                room.ready()
                self.non_ready_rooms.pop(ruleset)
                return room
            return None
        #if not create a new room
        new_room = self.create_room(ruleset)
        new_room.add_client(client, client_data)
        self.non_ready_rooms[ruleset] = new_room
        return None
    
    def create_room(self, ruleset):
        return Room(ruleset)