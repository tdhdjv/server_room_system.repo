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