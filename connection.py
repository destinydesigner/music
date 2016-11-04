import json
import socket
from tornado import gen, iostream
from request import Request
from commands import get_command_class
from errors import UnsupportedCommandError


class Connection(object):
    count = 0

    def __init__(self, stream):
        super(Connection, self).__init__()
        Connection.count += 1
        self.client_id = Connection.count
        self.stream = stream

        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self.stream.set_close_callback(self.on_disconnect)

    @gen.coroutine
    def on_disconnect(self):
        self.log("disconnected")
        yield []

    @gen.coroutine
    def read_cmd(self):
        try:
            while True:
                line = yield self.stream.read_until(b'\n')
                self.log('got |%s|' % line.decode('utf-8').strip())
                req = Request(json.loads(line))
                self.dispatch_cmd(req)
        except iostream.StreamClosedError:
            pass

    @gen.coroutine
    def on_connect(self):
        raddr = 'closed'
        try:
            raddr = '%s:%d' % self.stream.socket.getpeername()
        except Exception:
            pass
        self.log('new, %s' % raddr)

        yield self.read_cmd()

    def log(self, msg):
        print(
            '[connection %d] %s' % (self.client_id, msg)
        )

    def dispatch_cmd(self, request):
        try:
            klass = get_command_class(request.cmd)
        except UnsupportedCommandError:
            self.reply("Unsupported command")
            return

        handler = klass(self, request)
        handler.run()

    @gen.coroutine
    def reply(self, message):
        yield self.stream.write(message + '\n')
