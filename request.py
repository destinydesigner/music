import json
from errors import ParameterMissing, DataFormatError


class Request(object):
    def __init__(self, data):
        if not data:
            raise DataFormatError
        self.data = json.loads(data)
        if not isinstance(self.data, dict):
            raise DataFormatError

    def __getattr__(self, key):
        try:
            val = self.data[key]
            if key == 'channel_id':
                return long(val)
            return val
        except Exception as e:
            raise ParameterMissing(str(e))
