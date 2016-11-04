import json


class Request(object):
    def __init__(self, data):
        try:
            self.data = json.loads(data)
        except Exception as e:
            self.data = {
                'cmd': -1,
                'error': -1,
                'message': str(e),
            }
            self.response = self.data

    def __getattr__(self, key):
        return self.data[key]
