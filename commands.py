from datetime import datetime
from errors import (
    UnsupportedCommandError, UserDoesNotExist, AlreadyInChannel,
    PleaseQuitChannel, ChannelDoesNotExist)
from models import User, Channel, Song


class Command(object):
    cmd_id = None

    def __init__(self, connection, request, *args, **kwargs):
        self.connection = connection
        self.request = request
        self.response = request.data.copy()
        self.response.update({
            'error': 0,
            'message': 'success',
        })

    def run(self):
        self.execute()
        self.reply()

    def reply(self):
        self.connection.reply(self.response)


class Output(Command):
    cmd_id = -1

    def execute(self):
        pass


class Register(Command):
    cmd_id = 1

    def execute(self):
        try:
            user = User.get(self.request.client_id)
            user.connection = self.connection
            User.update(user)
            self.response.update({
                "user": user.data
            })
        except UserDoesNotExist:
            user = User(
                self.request.client_id,
                self.request.user_name,
                self.request.icon_id,
                self.connection,
            )
            self.response.update({
                "user": user.data
            })
            self.connection.client_id = self.request.client_id


class RetrieveChannels(Command):
    cmd_id = 2

    def execute(self):
        self.response.update({
            'channel_list': Channel.all(),
        })


class CreateChannel(Command):
    cmd_id = 3

    def execute(self):
        user = User.get(self.request.client_id)
        if user.channel:
            if user.client_id == user.channel.owner.client_id:
                self.construct_response(user.channel)
            else:
                raise AlreadyInChannel()
        else:
            channel = Channel(
                channel_name=self.request.channel_name,
                owner=user,
                song_play_time=self.request.song_play_time,
            )
            user.channel = channel
            self.construct_response(channel)

    def construct_response(self, channel):
        self.response.update({
            'channel': channel.data,
        })


class EnterChannel(Command):
    cmd_id = 4

    def execute(self):
        user = User.get(self.request.client_id)
        if user.channel:
            if user.channel.channel_id == long(self.request.channel_id):
                self.construct_response(user.channel)
                return
            raise PleaseQuitChannel()

        channel = Channel.get(self.request.channel_id)
        channel.members[user.client_id] = user
        user.channel = channel
        self.construct_response(user.channel)

    def construct_response(self, channel):
        self.response.update({
            'channel': channel.data,
        })


class TogglePlay(Command):
    cmd_id = 5

    def execute(self):
        user = User.get(self.request.client_id)
        if not user.channel:
            raise ChannelDoesNotExist
        self.response.update({
            'playing': not self.request.current_playing,
        })
        user.channel.notify_members(self.response)


class RetrieveSongs(Command):
    cmd_id = 11

    def execute(self):
        self.response.update({
            "song_list": Song.all(),
        })


class SynchronizeTime(Command):
    cmd_id = 102

    def __init__(self, connection, request, start_time, *args, **kwargs):
        super(SynchronizeTime, self).__init__(connection, request)
        self.start_time = start_time

    def execute(self):
        self.response.update({
            'server_processing_time': (
                datetime.now() - self.start_time).microseconds,
        })


class SystemDumpUser(Command):
    cmd_id = -2

    def execute(self):
        self.response.update({
            "users": User.all(),
        })


COMMAND_MAP = {
    -2: SystemDumpUser,
    -1: Output,
    1: Register,
    2: RetrieveChannels,
    3: CreateChannel,
    4: EnterChannel,
    5: TogglePlay,
    11: RetrieveSongs,
    102: SynchronizeTime,
}


def get_command_class(cmd_id):
    if cmd_id not in COMMAND_MAP:
        raise UnsupportedCommandError()
    return COMMAND_MAP[cmd_id]
