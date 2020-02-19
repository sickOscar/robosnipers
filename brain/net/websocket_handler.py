import tornado.websocket
import time
import uuid
from net.socket_registry import SocketRegistry

class WebSocketHandler(tornado.websocket.WebSocketHandler):

    clients = {}

    '''
    This class handles the websocket channel
    '''
    @classmethod
    def route_urls(cls):
        return [(r'/',cls, {}),]

    @classmethod
    def broadcast(cls, message):
        for client in WebSocketHandler.clients:
            client.write_message(message)
    
    def simple_init(self):
        self.id = uuid.uuid4()
        self.last = time.time()
        self.stop = False
        
    
    def open(self):
        '''
            client opens a connection
        '''
        self.simple_init()

        registry = SocketRegistry.get_instance()
        registry.add_socket(self)

        print("New client connected")
        self.write_message("You are connected (uuid " + str(self.id) + ")")

        # self.producer = Producer(self)
        # self.producer.start()
        
    def on_message(self, message):
        '''
            Message received on the handler
        '''
        print("received message {}".format(message))
        self.write_message("You said {}".format(message))
        self.last = time.time()
    
    def on_close(self):
        '''
            Channel is closed
        '''
        print("connection is closed")
        # producer.stop()
        # self.loop.stop()
    
    def check_origin(self, origin):
        return True
