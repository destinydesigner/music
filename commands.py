from errors import UnsupportedCommandError, UserDoesNotExist
from models import User


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

    def reply(self):
        self.connection.reply(self.response)


class Register(Command):
    cmd_id = 1

    def execute(self):
        try:
            user = User.get_user(self.request.client_id)
            self.response.update({
                "user": user.data
            })
        except UserDoesNotExist:
            user = User(
                self.request.client_id,
                self.request.user_name,
                self.request.icon_id,
            )
            self.response.update({
                "user": user.data
            })


class SystemDumpUser(Command):
    cmd_id = -2

    def execute(self):
        users = User.USER_POOL
        result = []
        for client_id, user in users.items():
            result.append(user.data)
        self.response.update({
            "users": result
        })


COMMAND_MAP = {
    -2: SystemDumpUser,
    -1: Output,
    1: Register,
}


def get_command_class(cmd_id):
    if cmd_id not in COMMAND_MAP:
        raise UnsupportedCommandError()
    return COMMAND_MAP[cmd_id]
