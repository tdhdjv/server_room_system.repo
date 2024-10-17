'''
Client class in charge of
1. recieving data to server
2. sending data to server 
3. handling responses from the server
'''
import socket
from ..utils import data_handler
from .protocols import Protocol
from threading import Thread
from dataclasses import dataclass

@dataclass
class ClientData:
    ID:int
    ADDRESS:tuple

class Client:
    data:ClientData
    ready = False
    running = True

    def run(self, host, port) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        #recieve client data
        packet = data_handler.decode(self.client.recv(1024))
        self.data = packet['data']

        #threading
        recieve_thread = Thread(target=self.recieve)
        main_thread = Thread(target=self.main, daemon=True)
        recieve_thread.start()
        main_thread.start()
        
        #ends the server when it stops recieving data
        recieve_thread.join()

        self.client.close()

    def recieve(self):
        while self.running:
            response = self.client.recv(1024)
            packet = data_handler.decode(response)

            protocol = packet['protocol']
            data = packet['data']

            #prebuilt commands
            if protocol == Protocol.Response.COMMAND:
                if data == 'close':
                    self.running = False
                if data == 'room ready!':
                    self.ready = True
            
            self.process_data(protocol, data)

    def quit(self):
        self.client.send(data_handler.encode(Protocol.Request.COMMAND, 'quit'))

    def send(self, protocol:str, data):
        self.client.send(data_handler.encode(protocol, data))

    def main(self):
        '''
        Implementation is up to subclass
        '''
        pass

    def process_data(self, protocol, data):
        '''
        Implementation is up to subclass
        '''
        pass

if __name__ == "__main__":
    client = Client()
    client.run('127.0.0.1', 1234)