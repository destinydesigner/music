import json
import uuid
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
            client_id = str(uuid.uuid4())
            yield self.stream.write(
                json.dumps({
                    "cmd": 1,
                    "client_id": client_id,
                    "user_name": "sf",
                    "icon_id": "sf",
                }) + '\n'
            )
            yield self.stream.write(
                json.dumps({
                    "cmd": 3, "client_id": client_id, "channel_name": "sf",
                    "song_play_time": 0,
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
                    "cmd": 4, "client_id": client_id, "channel_id": channel_id
                }) + '\n'
            )

            while True:
                line = yield self.stream.read_until(
                    b"\n")
                print line

    def callback(self, data):
        self.stream.read_until(b"\n", callback=self.callback)


def main():
    client = Client('127.0.0.1', 8008)
    client.start()

if __name__ == "__main__":
    main()
    ioloop.IOLoop.current().start()
