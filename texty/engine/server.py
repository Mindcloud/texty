from texty.engine import story
from tornado import web
from tornado import websocket
from tornado import ioloop
from tornado import httpserver
from tornado import template
import logging
import re

class HTMLClientHandler(web.RequestHandler):
    """
    This handler takes care of the HTML Client Application serving.
    """
    loader = template.Loader('texty/client-data/templates')

    def get(self):
        # serve base template
        s = story.Story.get()
        title = '%s %s' % (s.__name__, s.__version__)
        html = self.loader.load('base.html').generate(story=title)
        self.write(html)


class Connection(websocket.WebSocketHandler):
    """
    This simple handler wraps the tornado WebSocketHandler and hands off messages to our MUD server.
    """
    def open(self, token):
        self.application.MUD.connect(self, int(token))

    def on_message(self, data):
        self.application.MUD.data(self, data)

    def on_close(self):
        self.application.MUD.disconnect(self)

    def on_write(self, data):
        return data

    def send(self, data):
        data = self.on_write(data)
        return self.write_message(data)

    def check_origin(self, origin):
        return True


class MUD(object):
    """
    Main server class that wraps all tornado websocket communcation.
    """
    # event handlers
    def on_connect(self, connection, token): pass
    def on_disconnect(self, connection): pass
    def on_read(self, connection, data): pass

    def __init__(self):
        # connection tracking
        self.connections = dict()
        self.serial = 0
        # tornado objects
        self.app = web.Application([
            (r'/', HTMLClientHandler),
            (r'/websocket/(.*)', Connection),
            (r'/static/(.*)', web.StaticFileHandler, {'path': 'texty/client-data/static/'})
        ])
        # add a reference to this object so we can access it from handlers
        self.app.MUD = self

    def start(self, port):
        """
        Start the server.
        """
        self.app.listen(port)

    def stop(self):
        pass

    def connect(self, connection, token=None):
        """
        Player has connected.
        """
        # set id to next serial and increment
        id = self.serial = self.serial + 1
        # save reference
        self.connections[id] = connection
        self.connections[id].id = id
        # fire event
        self.on_connect(connection, token)

    def disconnect(self, connection):
        """
        Player has disconnected.
        """
        # fire event
        self.on_disconnect(connection)
        # remove connection from list
        id = connection.id
        if id in self.connections:
            del self.connections[id]

    def data(self, connection, data):
        """
        Received data from a connection. Clean it up and pass it to application.
        """
        # truncate incoming data to 100 chars
        # remove all but whitelisted characters
        data = data[:100]
        data = re.sub('[^\w\d\-\?,.!:;" ]', '', data)
        data = data.strip()

        # fire event
        if data:
            self.on_read(connection, data)

    def broadcast(self, message, exclude=None):
        """
        Broadcast a message to all connections.
        """
        if exclude == None:
            exclude = []
        for (id, connection) in self.connections.items():
            if connection not in exclude:
                connection.send(message)
