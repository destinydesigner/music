class BaseException(Exception):
    ERROR = None
    DEFAULT_MESSAGE = 'Unknown error'

    def __init__(self, message=None):
        self.message = message


class UnsupportedCommandError(BaseException):
    ERROR = -1
    DEFAULT_MESSAGE = "Unsupported command"


class DataFormatError(BaseException):
    ERROR = 1
    DEFAULT_MESSAGE = 'No json object'


class ParameterMissing(BaseException):
    ERROR = 2
    DEFAULT_MESSAGE = "Parameter Missing"

    def __init__(self, message=None):
        super(ParameterMissing, self).__init__(message)
        self.message = "Parameter %s is missing." % (message)


class UserDoesNotExist(BaseException):
    ERROR = 100
    DEFAULT_MESSAGE = "User does not exist"


class AlreadyInChannel(BaseException):
    ERROR = 101
    DEFAULT_MESSAGE = "This user is already in a channel"


class PleaseQuitChannel(BaseException):
    ERROR = 102
    DEFAULT_MESSAGE = "Please quit channel first."


class ChannelDoesNotExist(BaseException):
    ERROR = 103
    DEFAULT_MESSAGE = "Channel does not exist"


class UserIsNotInAnyChannel(BaseException):
    ERROR = 104
    DEFAULT_MESSAGE = "User is not in any channel"


class PatternDoesNotExist(BaseException):
    ERROR = 105
    DEFAULT_MESSAGE = "Pattern does not exist"
