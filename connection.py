import json
import socket
from tornado import gen, iostream
from request import Request
from commands import get_command_class
from decorators import handle_dispatch_exceptions
from errors import DataFormatError


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
    def read_data(self):
        try:
            while True:
                line = yield self.stream.read_until(b'\n')
                self.log('got <= |%s|' % line.decode('utf-8').strip())
                try:
                    request = self.parse(line.strip())
                except:
                    continue
                self.dispatch_cmd(request)
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

        yield self.read_data()

    def log(self, msg):
        print(
            '[connection %d] %s' % (self.client_id, msg)
        )

    def parse(self, line):
        try:
            return Request(line)
        except DataFormatError as e:
            resp = {
                'data': line
            }
            resp.update({
                "error": e.ERROR,
                "message": e.DEFAULT_MESSAGE if not e.message else e.message,
            })
            self.reply(resp)
            raise

    @handle_dispatch_exceptions
    def dispatch_cmd(self, request):
        klass = get_command_class(request.cmd)
        handler = klass(self, request)
        handler.run()

    @gen.coroutine
    def reply(self, data):
        try:
            message = json.dumps(data)
        except:
            import traceback
            print traceback.format_exc()
            message = data
        self.log('put => |%s|' % message)
        yield self.stream.write(message + '\n')
