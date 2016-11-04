from errors import UnsupportedCommandError


class Command(object):
    cmd_id = None

    def __init__(self, connection, request):
        self.connection = connection
        self.request = request

    def run(self):
        print "handle cmd %d" % (self.cmd_id)
        self.reply()


class Output(Command):
    cmd_id = -1

    def reply(self):
        self.connection.reply(self.request.response)


class Register(Command):
    cmd_id = 1

    def reply(self):
        self.connection.reply({
            'cmd': self.request.cmd,
            'error': 0,
            'message': 'success, cmd %d' % (self.cmd_id)
        })


COMMAND_MAP = {
    -1: Output,
    1: Register,
}


def get_command_class(cmd_id):
    if cmd_id not in COMMAND_MAP:
        raise UnsupportedCommandError()
    return COMMAND_MAP[cmd_id]
