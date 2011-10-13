#import libraries.tornado as tornado
import tornado.httpserver
import tornado.ioloop
#import tornado.process
#import tornado.netutil
import settings
import routes

TORNADO_APP = tornado.web.Application(routes.ROUTES, **settings.SERVER_SETTINGS)

class Server(object):
    def __init__(self, port):
        self.logger = settings.get_logger(settings.LOG, self.__class__.__name__)
        #sockets = tornado.netutil.bind_sockets(port)
        #tornado.process.fork_processes(0)
        server = tornado.httpserver.HTTPServer(TORNADO_APP)
        server.bind(port) 
        server.start()
        settings.startup()
        self.logger.debug("Server Started: %s" % port)
        tornado.ioloop.IOLoop.instance().start()
