from errors import (
    UserDoesNotExist, ChannelDoesNotExist)


class BaseObject(object):
    pass


class User(BaseObject):
    USER_POOL = {}

    def __init__(self, client_id=None, user_name=None, icon_id=None,
                 *args, **kwargs):
        self.client_id = client_id
        self.user_name = user_name
        self.icon_id = icon_id
        self.channel = None
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
        }


class Channel(BaseObject):
    CHANNEL_POOL = {}

    def __init__(self, channel_name=None, owner=None):
        self.channel_id = id(self)
        self.channel_name = channel_name
        self.now_playing_song_id = None
        self.song_list = []
        self.owner = owner
        self.CHANNEL_POOL[self.channel_id] = self

    @classmethod
    def get(cls, channel_id):
        try:
            return cls.CHANNEL_POOL[channel_id]
        except:
            raise ChannelDoesNotExist

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
            'song_list': self.song_list,
            'owner': self.owner.data,
        }


class Song(BaseObject):
    SONG_POOL = {
    }

    @classmethod
    def all(cls):
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
