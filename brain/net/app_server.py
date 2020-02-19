import tornado.web
import tornado.httpserver
import tornado.ioloop
from net.websocket_handler import WebSocketHandler
from tornado.options import define, options

define('port', default=4041, help='port to listen on')

class AppServer:

    def __init__(self):
        self.app = tornado.web.Application(WebSocketHandler.route_urls())

        self.server = tornado.httpserver.HTTPServer(self.app)
        self.server.listen(options.port)

    def start(self):
        #setup the server
        print('App Started')

        #start io/event loop
        tornado.ioloop.IOLoop.instance().start()
