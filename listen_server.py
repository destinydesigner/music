import logging as logger
from tornado import tcpserver, gen
from connection import Connection
from models import Channel


class ListenServer(tcpserver.TCPServer):
    def __init__(self, *args, **kwargs):
        super(ListenServer, self).__init__(*args, **kwargs)
        logger.info("ListenServer.__init__")
        self.io_loop.add_future(
            gen.coroutine(Channel.synchronize_playing)(),
            lambda f: f.result(),
        )

    @gen.coroutine
    def handle_stream(self, stream, address):
        """
        Called for each new connection, stream.socket is
        a reference to socket object
        """
        connection = Connection(stream)
        yield connection.on_connect()
