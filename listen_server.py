from tornado import tcpserver, gen
from connection import Connection


class ListenServer(tcpserver.TCPServer):
    """
    def __init__(self, *args, **kwargs):
        super(ListenServer, self).__init__(*args, **kwargs)
        self.io_loop.add_future(
            ConnectionPool.instance().push_channels(self.io_loop),
            ConnectionPool.instance().push_done,
        )
        """

    @gen.coroutine
    def handle_stream(self, stream, address):
        """
        Called for each new connection, stream.socket is
        a reference to socket object
        """
        connection = Connection(stream)
        yield connection.on_connect()
