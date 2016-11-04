import json
from tornado import tcpclient, ioloop, gen
from request import Request


class Client(object):
    def __init__(self, host, port):
        self.stream = None
        self.host = host
        self.port = port

    @gen.coroutine
    def start(self):
        if self.stream is None:
            self.stream = yield tcpclient.TCPClient().connect(
                self.host, self.port)
            yield self.stream.write(
                json.dumps({
                    "cmd": 1,
                    "client_id": "sf",
                    "user_name": "sf",
                    "icon_id": "sf",
                }) + '\n'
            )
            yield self.stream.write(
                json.dumps({
                    "cmd": 3, "client_id": "sf", "channel_name": "sf",
                }) + '\n'
            )
            while True:
                line = yield self.stream.read_until(
                    b"\n")
                req = Request(line)
                if req.cmd == 3:
                    channel_id = long(req.channel['channel_id'])
                    break
            yield self.stream.write(
                json.dumps({
                    "cmd": 4, "client_id": "sf", "channel_id": channel_id
                }) + '\n'
            )

    def callback(self, data):
        self.stream.read_until(b"\n", callback=self.callback)


def main():
    client = Client('127.0.0.1', 8008)
    client.start()

if __name__ == "__main__":
    main()
    ioloop.IOLoop.current().start()
