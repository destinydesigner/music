import json
import socket
from datetime import datetime
from tornado import gen, iostream
from request import Request
from commands import get_command_class
from decorators import handle_dispatch_exceptions
from errors import DataFormatError
from models import User, Channel


class Connection(object):
    count = 0

    def __init__(self, stream):
        super(Connection, self).__init__()
        Connection.count += 1
        self.id = Connection.count
        self.client_id = None
        self.stream = stream
        self.start_time = None

        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self.stream.set_close_callback(self.on_disconnect)

    @gen.coroutine
    def on_disconnect(self):
        self.log("disconnected")
        user = User.get(self.client_id)
        if user.channel:
            try:
                del user.channel.members[self.client_id]
            except:
                import traceback
                print traceback.format_exc()

            if user.client_id == user.channel.owner.client_id:
                try:
                    del Channel.CHANNEL_POOL[user.channel.channel_id]
                except:
                    import traceback
                    print traceback.format_exc()
        del User.USER_POOL[user.client_id]

        yield []

    @gen.coroutine
    def on_connect(self):
        raddr = 'closed'
        try:
            raddr = '%s:%d' % self.stream.socket.getpeername()
        except Exception:
            pass
        self.log('new, %s' % raddr)

        yield self.read_data()

    @gen.coroutine
    def read_data(self):
        try:
            while True:
                line = yield self.stream.read_until(b'\n')
                self.start_time = datetime.now()
                self.log('got <= |%s|' % line.decode('utf-8').strip())
                try:
                    request = self.parse(line.strip())
                except:
                    continue
                self.dispatch_cmd(request)
        except iostream.StreamClosedError:
            pass

    def log(self, msg):
        print(
            '[connection %d] %s' % (self.id, msg)
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
        handler = klass(self, request, self.start_time)
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
