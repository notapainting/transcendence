from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.validators import UniqueValidator

from . import models
import io

from django.utils import timezone

from channels.db import database_sync_to_async

def parse_json(data):
    return JSONParser().parse(io.BytesIO(data))


def render_json(data):
        return (JSONRenderer().render(data))

# field
class UserRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance
    def to_representation(self, value):
        return str(value)
    def to_internal_value(self, data):
        return models.ChatUser.objects.get(name=data)

# serializer
class   BaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        # if hasattr(self, 'initial_data') is True and self.initial_data is not None:
        #     self.initial_data = self.parse_json()

        if fields is not None:
            fields = fields.split()
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def parse_json(self):
        return JSONParser().parse(io.BytesIO(self.initial_data))

    def render_json(self):
        return (JSONRenderer().render(self.data)) 


class ChatUserSerializer(BaseSerializer):
    class Meta:
        model = models.ChatUser
        fields = ['name', 'contact_list', 'blocked_list', 'groups']
        extra_kwargs = {
                            'contact_list': {'required': False},
                            'blocked_list': {'required': False},
                            'groups': {'required': False}
                        }


class ChatMessageSerializer(BaseSerializer):
    class Meta:
        model = models.ChatMessage
        fields = ['id', 'author', 'group', 'date', 'respond_to', 'body']
        extra_kwargs = {'date': {'format' : '%Y-%m-%dT%H:%M:%S.%fZ%z', 'default':timezone.now}}

    author = UserRelatedField(queryset=models.ChatUser.objects.all(), required=False)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # print("ret is")
        # print(ret)
        # ret['id'] = str(ret['id'])
        return ret


class ChatGroupSerializer(BaseSerializer):
    class Meta:
        model = models.ChatGroup
        fields = ['id', 'name', 'members', 'messages']

    members = UserRelatedField(queryset=models.ChatUser.objects.all(), many=True)
    messages = ChatMessageSerializer(many=True, required=False, fields='id author date body')


class EventSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=50)
    data = serializers.DictField(child=serializers.CharField())

class MessageEventSerializer(EventSerializer):
    pass

content = b'{"id":"08c5e0ae-69b8-418e-84c5-9010ef8d1d1e","name":"luciole"}'
new = b'{"id":"62e661f9-a68e-4558-b833-339a90cecd01", "name":"xueyi"}'
