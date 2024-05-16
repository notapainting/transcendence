#chat/utils.py

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from io import BytesIO


import chat.models as mod
import chat.enums as enu

def create_private_conv(user1, user2):
    pgroup = mod.Group.objects.create(name='@')
    pgroup.members.set([user1, user2], through_defaults={'role':mod.GroupShip.Roles.WRITER})
    pgroup.members.add(mod.User.objects.get(name=enu.SpecialUser.ADMIN), through_defaults={'role':mod.GroupShip.Roles.OWNER})
    return pgroup


def parse_json(data):
    return JSONParser().parse(BytesIO(data))


def render_json(data):
        return (JSONRenderer().render(data))

def cleaner(data, key=None):
    ret = []
    if key is not None:
        for element in data:
            ret.append(element[key])
    else:
        for element in data:
            ret.append(element)
    return ret


