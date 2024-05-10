# chat/consumers.py

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError
from channels.exceptions import DenyConnection


# Get an instance of a logger
import logging
logger = logging.getLogger('django')



import chat.serializers as ser
import chat.models as mod
import chat.enums as enu


from channels.db import database_sync_to_async

    # get from db conv list
    # group_add cs to conv (group)
    # send to cl chat history
    # limit to 10 old conv/active user
    # test active user : db/ping cs, middleware list, auth ?

# handle db errors
# @database_sync_to_async
# def handle_message(username, data):
#     ser = get_serializer('chat.message')
#     ms = ser(data=data, author=username)
#     ms.is_valid(raise_exception=True)
#     ms.create(ms.validated_data)
#     return ms.data

CONTACT_ALL = 'contacts blockeds blocked_by invitations invited_by'







async def validate_data(username, data):
    type = data.get('type', None)
    data = data.get('data', None)
    if type is None or data is None:
        raise ValidationError("invalid event")
    data['author'] = username
    if type in enu.Event.val(enu.Event):
        return type
    else:
        raise ValidationError(f"event type unknow : {type}")


async def get_serializer(type):
    serializers = {
        enu.Event.Message.TEXT : ser.Message,
        enu.Event.Status.UPDATE : ser.EventStatus,
        enu.Event.Contact.UPDATE : ser.EventContact,
        enu.Event.Group.CREATE : ser.EventGroupCreate,
        enu.Event.Group.CREATE_PRIVATE : ser.EventGroupCreatePrivate,
        enu.Event.Group.UPDATE : ser.EventGroupUpdate,
    }
    return serializers[type]

@database_sync_to_async
def serializer_handler(serializer, data):
    ser = serializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.create(ser.validated_data)
    return ser.data


def create_private_conv(user1, user2):
    pgroup = mod.Group.create(name='@')
    pgroup.members.add(enu.SpecialUser.ADMIN, through_defaults={'role':mod.GroupShip.Roles.OWNER})
    pgroup.members.add(user1, through_defaults={'role':mod.GroupShip.Roles.WRITER})
    pgroup.members.add(user2, through_defaults={'role':mod.GroupShip.Roles.WRITER})
    return pgroup

class ChatConsumer(AsyncJsonWebsocketConsumer):

    group_list = []

    @database_sync_to_async
    def auth(self):
        name = self.scope['cookies'].get('userName')
        try:
            return mod.User.objects.get(name=name)
        except ObjectDoesNotExist:
            raise DenyConnection

    @database_sync_to_async
    def get_group_summary(self):
        data = {}
        data['type'] = 'group.summary'
        data['data'] = ser.Group(self.user.groups.all(), many=True).data
        for group in data['data']:
            self.group_list.append(group['id'])
            group['messages'] = group['messages'][:2]
        return data


    async def connect(self):
        self.user = await self.auth()

        #accept connectiont to client
        subprotocol = self.scope.get('subprotocol')
        await self.accept(subprotocol)
        logger.info("%s Connected!", self.user.name)

        # send group summary
        group_summary = await self.get_group_summary()
        await self.send_json(group_summary)

        # add user to channel groups
        await self.channel_layer.group_add(self.user.name, self.channel_name)#attention au name
        for id in self.group_list:
            await self.channel_layer.group_add(id, self.channel_name)

        # send status update
        # fetch status update

    async def disconnect(self, close_code):
        for id in self.group_list:
            await self.channel_layer.group_discard(id, self.channel_name)
        await self.channel_layer.group_discard(self.user.name, self.channel_name)
        logger.info("%s Quit...", self.user.name)

    async def dispatch(self, message):
        print(f'msg type : {message['type']}')
        await super().dispatch(message)


    @database_sync_to_async
    def get_contact_list(self, fields='contacts'):
        return ser.User(self.user, fields=fields).data


    @database_sync_to_async
    def contact_handler(self, data):
        try :
            author = mod.User.objects.get(name=self.user.name)
            target = mod.User.objects.get(name=data['name'])
            if author == target:
               raise ValidationError('forbidden self operation on contact', code=403)

            if data['operation'] == enu.Operations.REMOVE:
                author.delete_relation(target)
                target_rel = target.get_relation(author)
                if target_rel is not None and target_rel != mod.Relation.Types.BLOCK:
                    target.delete_relation(author)
                    # unblock p-conv

            elif data['operation'] == enu.Operations.BLOCK:
                # block p-conv
                author.update_relation(target, mod.Relation.Types.BLOCK)
                if target.get_relation(author) != mod.Relation.Types.BLOCK:
                    target.delete_relation(author)

            else: # data['operation'] == enu.Operations.CONTACT or enu.Operations.INVIT
                target_rel = target.get_relation(author)
                if target_rel == mod.Relation.Types.BLOCK:
                    raise ValidationError('your blocked, dont do this', code=403)
                elif target_rel == mod.Relation.Types.INVIT:
                    author.update_relation(target, mod.Relation.Types.COMRADE)
                    target.update_relation(author, mod.Relation.Types.COMRADE)
                    data['operation'] = enu.Operations.CONTACT
                else:
                    author.update_relation(target, mod.Relation.Types.INVIT)
                    data['operation'] = enu.Operations.INVIT

            return data
        except ObjectDoesNotExist:
            raise ValidationError('target not found', code=404)
        except ValidationError:
            raise 
        except BaseException as e:
            print(e.args[0])
            raise ValidationError('INTERNAL', code=500)

    @database_sync_to_async
    def group_create_handler(self, data):
        pass

    @database_sync_to_async
    def group_create_private_handler(self, data):
        print(data)

# contact -> username !! selfgroups ?? 
    async def client_event_handler(self, type, data):
        ms = {}
        ms['type'] = type
        ms['data'] = data
        if type == enu.Event.Message.TEXT:
            await self.channel_layer.group_send(ms['data']['group'], ms)
        elif type == enu.Event.Message.FETCH:
            pass
        elif type == enu.Event.Message.GAME:
            pass
        elif type ==  enu.Event.Status.UPDATE:
            for contact in await self.get_contact_list():
                await self.channel_layer.group_send(contact, ms)
                await self.channel_layer.group_send(self.user.name, ms)
        elif type ==  enu.Event.Status.FETCH:
            pass
            # ?? 
        elif type ==  enu.Event.Contact.UPDATE:
            ret = await self.contact_handler(ms['data'])
            ms['data'] = ret
            await self.send_json(ms)
            await self.channel_layer.group_send(ms['data']['name'], ms)
        elif type == enu.Event.Group.CREATE:
            pass
        elif type == enu.Event.Group.CREATE_PRIVATE:
            await self.group_create_private_handler(ms['data'])
        elif type == enu.Event.Group.UPDATE:
            pass


    async def receive_json(self, text_data):
        print(f'text : {text_data}')
        try :
            type = await validate_data(username=self.user.name, data=text_data)
            serial = await get_serializer(type)
            ser_data = await serializer_handler(serial, text_data['data'])
            await self.client_event_handler(type, ser_data)

        except ValidationError as e:
                print(e.args[0])
                await self.send_json({"data": "fck u"})


    # Receive message from room group
    async def message_text(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def message_game(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def status_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def status_fetch(self, event):
        # Send message to WebSocket
        # should send back status_update
        await self.send_json(event)

    async def contact_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def group_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)
