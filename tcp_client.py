from tornado import tcpclient, ioloop, gen


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
            self.stream.read_until(b"\n", callback=self.callback)

    def callback(self, data):
        print data
        self.stream.read_until(b"\n", callback=self.callback)


def main():
    client = Client('127.0.0.1', 8008)
    client.start()

if __name__ == "__main__":
    main()
    ioloop.IOLoop.current().start()
