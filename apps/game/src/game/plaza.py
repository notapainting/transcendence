# game/plaza.py

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class Plaza(metaclass=Singleton):
    _users = {}

    def join(self, username, channel_name):
        Plaza._users[username] = channel_name

    def leave(self, username):
        if username in Plaza._users:
            del Plaza._users[username]

    def listing(self):
        return Plaza._users

    def translate(self, user):
        return Plaza._users.get(user)

    def found(self, user):
        return user in Plaza._users


plaza = Plaza()

