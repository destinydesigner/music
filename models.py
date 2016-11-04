import time
import logging as logger
from tornado import gen, iostream
from errors import (
    UserDoesNotExist, ChannelDoesNotExist)


class BaseObject(object):
    pass


class User(BaseObject):
    USER_POOL = {}

    def __init__(self, client_id=None, user_name=None, icon_id=None,
                 connection=None,
                 *args, **kwargs):
        self.client_id = client_id
        self.user_name = user_name
        self.icon_id = icon_id
        self.channel = None
        self.connection = connection
        self.USER_POOL[client_id] = self

    @classmethod
    def get(cls, client_id):
        try:
            return cls.USER_POOL[client_id]
        except:
            raise UserDoesNotExist

    @classmethod
    def all(cls):
        result = []
        for client_id, user in cls.USER_POOL.items():
            result.append(user.data)
        return result

    @property
    def data(self):
        return {
            "user_name": self.user_name,
            "client_id": self.client_id,
            "icon_id": self.icon_id,
            "channel_id": self.channel.channel_id if self.channel else None,
        }

    @classmethod
    def update(cls, user):
        cls.USER_POOL[user.client_id] = user


class Channel(BaseObject):
    CHANNEL_POOL = {}

    def __init__(self, channel_name=None, owner=None, song_play_time=None,
                 songs=None):
        self.channel_id = id(self)
        self.channel_name = channel_name
        self.owner = owner
        self.songs = songs[:]
        try:
            self.now_playing_song_id = songs[0].song_id
        except:
            self.now_playing_song_id = None
        self.members = {owner.client_id: owner}
        self.song_play_time = song_play_time
        self.server_start_time = time.time() * 1000
        self.CHANNEL_POOL[self.channel_id] = self

    @classmethod
    def update(cls, channel):
        cls.CHANNEL_POOL[channel.channel_id] = channel

    @classmethod
    def synchronize_playing(cls):
        for channel_id, channel in cls.CHANNEL_POOL.items():
            package = SyncPackage(channel=channel)
            channel.push_to_all(package.data)

    def notify_members(self, data):
        closed_user = []
        logger.debug(self.members)
        for client_id, user in self.members.items():
            # if client_id == self.owner.client_id:
            #     continue
            try:
                user.connection.reply(data)
            except iostream.StreamClosedError:
                user.connection.log('Stream closed')
                closed_user.append(client_id)

        for client_id in closed_user:
            del self.members[client_id]

        if not self.members:
            del self.CHANNEL_POOL[self.channel_id]

    def push_to_all(self, data):
        closed_user = []
        for client_id, user in self.members.items():
            try:
                user.connection.reply(data)
            except iostream.StreamClosedError:
                user.connection.log('Stream closed')
                closed_user.append(client_id)

        for client_id in closed_user:
            del self.members[client_id]

        if not self.members:
            del self.CHANNEL_POOL[self.channel_id]

    @staticmethod
    def push_channels_done(result):
        yield gen.sleep(1)

    @classmethod
    def get(cls, channel_id):
        try:
            return cls.CHANNEL_POOL[long(channel_id)]
        except:
            raise ChannelDoesNotExist

    def quit(self, client_id):
        try:
            del self.members[client_id]
        except:
            import traceback
            print traceback.format_exc()

        if client_id == self.owner.client_id:
            try:
                del Channel.CHANNEL_POOL[self.channel_id]
            except:
                import traceback
                print traceback.format_exc()

    @classmethod
    def all(cls):
        result = []
        for channel_id, channel in cls.CHANNEL_POOL.items():
            result.append(channel.data)
        return result

    @property
    def data(self):
        return {
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'now_playing_song_id': self.now_playing_song_id,
            'song_list': self.get_songs(),
            'owner': self.owner.data,
            'number_of_members': len(self.members),
            'song_play_time': self.get_song_play_time(),
        }

    def get_songs(self):
        result = []
        for song in self.songs:
            result.append({
                'song_id': song.song_id,
                'url': '',
            })
        return result

    def get_song_play_time(self):
        while True:
            yield int(
                self.song_play_time
                + (time.time() * 1000
                   - self.server_start_time)
            )

    def get_members(self):
        result = []
        for client_id, user in self.members.items():
            result.append(
                user.data,
            )
        return result


class Song(BaseObject):
    SONG_POOL = {
    }

    def __init__(self, song_id, url):
        self.song_id = song_id
        self.url = url

    @classmethod
    def all(cls):
        song_md5 = [
            'fcfcf63361d8486b637f0dfb8969f280',
            '5f9635394761f94c17599966a9b8d5fb',
            '09ee24cd60e00f1e5b03d96ef6be526b',
        ]
        for md5 in song_md5:
            cls.SONG_POOL[md5] = Song(md5, 'http://google.com')
        result = []
        for song_id, song in cls.SONG_POOL.items():
            result.append(song.data)
        return result

    @property
    def data(self):
        return {
            'song_id': self.song_id,
            'url': self.url,
        }


class Pattern(BaseObject):
    pass


class Mode(BaseObject):
    pass


class SyncPackage(BaseObject):
    def __init__(self, channel=None, pattern=None, *args, **kwargs):
        self.cmd = 100
        self.pattern = pattern
        self.channel = channel

    @property
    def data(self):
        return {
            'cmd': self.cmd,
            'pattern': self.pattern.data if self.pattern else None,
            'current_mode': 1,
            'song_play_time': self.channel.get_song_play_time(),
            'song_id': self.channel.now_playing_song_id,
        }
