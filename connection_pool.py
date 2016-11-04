import threading
from tornado import gen
from datetime import datetime


class ConnectionPool(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.pool = {}
        self.channels = {}

    @staticmethod
    def instance():
        if not hasattr(ConnectionPool, "_instance"):
            with ConnectionPool._instance_lock:
                if not hasattr(ConnectionPool, "_instance"):
                    ConnectionPool._instance = ConnectionPool()
        return ConnectionPool._instance

    def add_connection(self, connection):
        self.pool[connection.client_id] = connection

    @gen.coroutine
    def push_channels(self, io_loop):
        print "push_channels"
        for _id, connection in self.pool.items():
            yield connection.stream.write(str(datetime.now()) + '\n')
        yield gen.sleep(10)
        io_loop.add_future(
            self.push_channels(io_loop),
            self.push_done
        )

    def push_done(self, *args, **kwargs):
        print "Push done"
