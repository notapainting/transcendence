#chat/utils.py

import chat.models as mod
import chat.enums as enu

def create_private_conv(user1, user2):
    pgroup = mod.Group.objects.create(name='@')
    pgroup.members.set([user1, user2], through_defaults={'role':mod.GroupShip.Roles.WRITER})
    pgroup.members.add(mod.User.objects.get(name=enu.SpecialUser.ADMIN), through_defaults={'role':mod.GroupShip.Roles.OWNER})
    return pgroup

