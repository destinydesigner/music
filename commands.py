import logging as logger
from datetime import datetime
from errors import (
    UnsupportedCommandError, UserDoesNotExist, AlreadyInChannel,
    PleaseQuitChannel, ChannelDoesNotExist, UserIsNotInAnyChannel)
from models import User, Channel, Song, SyncPackage


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
            logger.info("Create new Channel")
            channel = Channel(
                channel_name=self.request.channel_name,
                owner=user,
                song_play_time=self.request.song_play_time,
                songs=self.request.songs,
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
                logger.debug("User already in this channel")
                self.construct_response(user.channel)
                return
            logger.debug("User in another channel, please quit first")
            raise PleaseQuitChannel()

        channel = Channel.get(self.request.channel_id)
        logger.debug("Got the channel")
        channel.members[user.client_id] = user
        logger.debug("Update the memebers of channel.")
        user.channel = channel
        Channel.update(channel)
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
        package = SyncPackage(channel=user.channel)
        user.channel.push_to_all(package.data)


class RetrieveMembers(Command):
    cmd_id = 6

    def execute(self):
        channel = Channel.get(self.request.channel_id)
        self.response.update({
            "member_list": channel.get_members(),
        })


class QuitChannel(Command):
    cmd_id = 7

    def execute(self):
        user = User.get(self.request.client_id)
        if not user.channel:
            raise UserIsNotInAnyChannel
        user.channel.quit(user.client_id)


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
    6: RetrieveMembers,
    7: QuitChannel,
    11: RetrieveSongs,
    102: SynchronizeTime,
}


def get_command_class(cmd_id):
    if cmd_id not in COMMAND_MAP:
        raise UnsupportedCommandError()
    logger.debug('Found cmd. Cmd: %d', cmd_id)
    return COMMAND_MAP[cmd_id]
