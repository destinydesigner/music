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
