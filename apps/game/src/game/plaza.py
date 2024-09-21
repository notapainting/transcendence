# game/plaza.py

import httpx

from logging import getLogger
logger = getLogger('base')


class PlazaException(Exception):
    pass

class PlazaNotFound(Exception):
    pass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class Plaza(metaclass=Singleton):
    _users = {}

    def join(self, username, channel_name):
        Plaza._users[username] = str(channel_name)

    def leave(self, username):
        if username in Plaza._users:
            del Plaza._users[username]

    def listing(self):
        return Plaza._users

    def translate(self, user, raise_exception=False):
        if raise_exception is False:
            return Plaza._users.get(user)
        else:
            if self.found(user):
                return Plaza._users.get(user)
            else:
                raise PlazaNotFound()

    def found(self, user):
        return user in Plaza._users


plaza = Plaza()

class TournamentCount(metaclass=Singleton):
    _id = 0;

    async def retrieve(self):
        if TournamentCount._id == 0:
            try:
                promise = await httpx.AsyncClient().get("http://blockchain:8000/register_match/")
                if promise.status_code == 200:
                    TournamentCount._id = promise.json()['last_tournament_id']
                    logger.info(f"id retrieved: {TournamentCount._id}")
                    if TournamentCount._id == None:
                        TournamentCount._id = 1
            except (httpx.HTTPError) as error:
                logger.critical(f"failed to send to blockchain, error : {error}")
        TournamentCount._id += 1
        return TournamentCount._id

tid_count = TournamentCount()
