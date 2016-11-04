class Request(object):
    def __init__(self, data):
        self.data = data

    def __getattr__(self, key):
        return self.data[key]
