class Registry:
    
    def __init__(self):
        self.sockets = {}
    
    def add_socket(self, socket):
        self.sockets[socket.id] = socket

    def remove_socket(self, id):
        pass

    def broadcast(self, message):
        for socket_id in self.sockets:
            # print('broadcast message to ' + str(socket_id))
            self.sockets[socket_id].write_message(message)