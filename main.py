import logging
import tornado.ioloop
from listen_server import ListenServer


logging.basicConfig(filename='example.log', level=logging.DEBUG)


def main():
    # configuration
    host = '0.0.0.0'
    port = 8008

    io_loop = tornado.ioloop.IOLoop.instance()

    # tcp server
    server = ListenServer(io_loop=io_loop)
    server.listen(port, host)
    print("Listening on %s:%d..." % (host, port))

    # infinite loop
    io_loop.start()


if __name__ == "__main__":
    main()
