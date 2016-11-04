import json


class Request(object):
    def __init__(self, data):
        try:
            self.data = json.loads(data)
            if not isinstance(self.data, dict):
                raise Exception("Please send a json object.")
        except Exception as e:
            self.data = {
                'cmd': -1,
                'error': -1,
                'message': str(e),
            }
            self.response = self.data

    def __getattr__(self, key):
        return self.data[key]
