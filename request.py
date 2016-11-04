import logging as logger
import json
from errors import ParameterMissing, DataFormatError


class Request(object):
    def __init__(self, data):
        if not data:
            raise DataFormatError
        if isinstance(data, str):
            self.data = json.loads(data)
        elif isinstance(data, dict):
            self.data = data
        else:
            raise DataFormatError

        if not isinstance(self.data, dict):
            raise DataFormatError

    def __getattr__(self, key):
        try:
            val = self.data[key]
            if key == 'channel_id':
                return long(val)
            if key == 'channel':
                logger.debug(type(val))
                return Request(val)
            if key == 'song_list':
                return [Request(s) for s in val]
            return val
        except Exception as e:
            raise ParameterMissing(str(e))
