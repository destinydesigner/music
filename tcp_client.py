#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import uuid
import logging
from tornado import tcpclient, ioloop, gen
from request import Request


logging.basicConfig(
    filename='client.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
)


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
                    "user_name": "Fang Guojian",
                    "icon_id": "sf",
                }) + '\n'
            )
            yield self.stream.write(
                json.dumps({
                    "cmd": 3,
                    "client_id": client_id,
                    "channel": {
                        "channel_name": "模式数据",
                        "song_play_time": 0,
                        "song_list": [
                            {
                                "song_id": 'fcfcf63361d8486b637f0dfb8969f280',
                            },
                            {
                                "song_id": '5f9635394761f94c17599966a9b8d5fb',
                            },
                            {
                                "song_id": '09ee24cd60e00f1e5b03d96ef6be526b',
                            }
                        ]
                    }
                }) + '\n'
            )
            while True:
                line = yield self.stream.read_until(
                    b"\n")
                req = Request(line)
                if req.cmd == 3:
                    channel_id = long(req.channel.channel_id)
                    break
            yield self.stream.write(
                json.dumps({
                    "cmd": 4, "client_id": client_id, "channel_id": channel_id
                }) + '\n'
            )

            yield gen.sleep(3)

            yield self.stream.write(
                json.dumps({
                    "cmd": 10,
                    "channel_id": channel_id,
                    "song_id": '09ee24cd60e00f1e5b03d96ef6be526b',
                    "song_play_time": 10000,
                }) + '\n'
            )

            while True:
                yield gen.sleep(3)

                yield self.stream.write(
                    json.dumps({
                        "cmd": 8,
                        "channel_id": channel_id,
                        "pattern": {
                            'member_index': 0,
                            "control_unit_list": [
                                {"volumn": 10, "delay": 5},
                                {"volumn": 10, "delay": 5},
                                {"volumn": 10, "delay": 5},
                            ],
                            'period': 10000,
                        },
                    }) + '\n'
                )

            while True:
                """
                yield self.stream.write(
                    json.dumps({
                        "cmd": 5,
                        "client_id": client_id,
                        "current_playing": flag,
                    }) + '\n'
                )
                yield gen.sleep(3)
                """

                try:
                    line = yield self.stream.read_until(
                        b"\n")
                    # logging.debug(line.strip())
                    print line.strip()
                except:
                    return

    def callback(self, data):
        self.stream.read_until(b"\n", callback=self.callback)


def main():
    client = Client('127.0.0.1', 8008)
    client.start()

if __name__ == "__main__":
    main()
    ioloop.IOLoop.current().start()
