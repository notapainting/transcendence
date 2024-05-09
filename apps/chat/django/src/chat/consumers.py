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


async def get_serializer(type):
    serializers = {
        enu.Event.Message.TEXT : ser.Message,
        enu.Event.Contact.UPDATE : ser.EventContact,
        enu.Event.Status.UPDATE : ser.EventStatus,
    }
    return serializers[type]



def resolve_invitation(author, target):
    if author.blocked_by.all().filter(name=target.name).exist():
        raise ValidationError('author is blocked', code=403)
    if author.blockeds.all().filter(name=target.name).exist():
        raise ValidationError('target is blocked by author.. dont be stupid plz', code=403)
    if author.invited_by.all().filter(name=target.name).exists():
        author.contacts.add(target)
        target.invitations.remove(author)
        return True
    else:
        author.invitations.add(target)
        return False

@database_sync_to_async
def serializer_handler(serializer, data):
    ser = serializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.create(ser.validated_data)
    return ser.data


async def validate_data(username, data):
    type = data.get('type', None)
    data = data.get('data', None)
    if type is None or data is None:
        raise ValidationError("invalid event")
    data['author'] = username
    if type in enu.Event:
        return type
    else:
        raise ValidationError(f"event type unknow : {type}")

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

    async def disconnect(self, close_code):
        for id in self.group_list:
            await self.channel_layer.group_discard(id, self.channel_name)
        await self.channel_layer.group_discard(self.user.name, self.channel_name)
        logger.info("%s Quit...", self.user.name)


    async def dispatch(self, message):
        print(f'msg type : {message['type']}')
        await super().dispatch(message)



    @database_sync_to_async
    def get_contact_list(self):
        contacts = ser.User(self.user, fields='contacts blockeds blocked_by invitations invited_by').data
        return contacts


# add contact / add invit -> return invit or if success contact
# add block -> return add block (same)
# del block -> return del block (same)
# del contact -> return del contact (same)
# del invit -> return del invit (same)
    # maj user from database
    @database_sync_to_async
    def contact_handler(self, data):
        op = data.get('operation', None)
        if op is None:
            raise ValidationError('missing operation field', code=400)
        try :
            author = mod.User.objects.get(name=self.user.name)
            target = mod.User.objects.get(name=data['name'])
            if author == target:
               raise ValidationError('forbidden self operation on contact', code=403)
            if data['relation'] == 'c':
                if op == 'a':
                    if resolve_invitation(author, target) is False:
                        data['relation'] = 'i'
                elif op == 'r':
                    author.contacts.remove(target)
            elif data['relation'] == 'b':
                if op == 'a':
                    author.contacts.remove(target)
                    author.invitations.remove(target)
                    target.invitations.remove(author)
                    author.blockeds.add(target)
                    # author.groups.all().filter(members=)
                    # find a way to select private conv easily
                elif op == 'r':
                    author.blockeds.remove(target)
            elif data['relation'] == 'i':
                if op == 'a':                   
                    if resolve_invitation(author, target) is True:
                        data['relation'] = 'c'
                elif op == 'r':
                    author.invitations.remove(target)
            return data

        except ObjectDoesNotExist:
            raise ValidationError('target not found', code=404)
        except ValidationError:
            raise 
        except BaseException as e:
            print(e.args[0])
            raise ValidationError('INTERNAL', code=500)

    # check if user is blocked ? 
    @database_sync_to_async
    def message_handler(self, data):
        author = mod.User.get(name=self.user.name)
        if author.groups.all().filter(id=data['group']).exist() is False:
            raise ValidationError('author not in group', code=403)

# contact -> username !! selfgroups ?? 
    async def event_handler(self, type, data):
        ms = {}
        ms['type'] = type
        ms['data'] = data
        if type == 'message.group':
            self.message_handler(ms['data'])
            await self.channel_layer.group_send(ms['data']['group'], ms)
        elif type == 'status.update':
            contacts = await self.get_contact_list();
            for contact in contacts:
                await self.channel_layer.group_send(contact, ms)
        elif type == 'contact.update':
            ret = await self.contact_handler(ms['data'])
            ms['data'] = ret
            await self.send_json(ms)
            ret['author'], ret['name'] = ret['name'], ret['author']
            print(ret)
            await self.channel_layer.group_send(ms['data']['author'], ms)


    async def receive_json(self, text_data):
        print(f'text : {text_data}')
        try :
            type = await validate_data(username=self.user.name, data=text_data)
            serial = await get_serializer(type)
            ser_data = await serializer_handler(serial, text_data['data'])
            await self.event_handler(type, ser_data)

        except ValidationError as e:
                print(e.args[0])
                await self.send_json({"data": "fck u"})


    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def status_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def contact_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)
