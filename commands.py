from errors import (
    UnsupportedCommandError, UserDoesNotExist, AlreadyInChannel,
    PleaseQuitChannel)
from models import User, Channel


class Command(object):
    cmd_id = None

    def __init__(self, connection, request):
        self.connection = connection
        self.request = request
        self.response = request.data.copy()
        self.response.update({
            'error': 0,
            'message': 'success',
        })

    def run(self):
        print "handle cmd %d" % (self.cmd_id)
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
                owner=user)
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
        user.channel = channel

    def construct_response(self, channel):
        self.response.update({
            'channel': channel.data,
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
}


def get_command_class(cmd_id):
    if cmd_id not in COMMAND_MAP:
        raise UnsupportedCommandError()
    return COMMAND_MAP[cmd_id]
