from errors import UserDoesNotExist


class BaseObject(object):
    pass


class User(BaseObject):
    USER_POOL = {}

    def __init__(self, client_id=None, user_name=None, icon_id=None,
                 *args, **kwargs):
        self.client_id = client_id
        self.user_name = user_name
        self.icon_id = icon_id
        self.USER_POOL[client_id] = self

    @classmethod
    def get_user(cls, client_id):
        try:
            return cls.USER_POOL[client_id]
        except:
            raise UserDoesNotExist

    @property
    def data(self):
        return {
            "user_name": self.user_name,
            "client_id": self.client_id,
        }


class Channel(BaseObject):
    pass


class Pattern(BaseObject):
    pass


class Mode(BaseObject):
    pass
