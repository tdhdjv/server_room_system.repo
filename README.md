# Server Room System
This project aims to create a server room system where a room is an isolated enviornment where only clients can only communicate to the clients in the same server.
## Usage
Example Server
```python
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
```

Example Client

```python
# myclient.py

from server_room_system.src import *

class MyClient(Client):

    #this function is called once when the client is run
    def main(self):
        #send to server that they are 
        message = ''
        while not message.isdigit():
            message = input('Client Count:')
        client_count = int(message)
        self.send(Protocol.Request.ROOM_RULSET, RuleSet(client_count))

        while True:
            message = input()
            if message.startswith('/'):
                message = message.removeprefix('/')
                if message == 'quit':
                    self.quit()
            else:
                self.send(Protocol.Request.MESSAGE, message)

if __name__ == "__main__":
    client = MyClient()
    client.run('127.0.0.1', 1234)
```

Example Room 
```python
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
```
