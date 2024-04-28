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
        fields = ['name', 'contacts', 'blockeds', 'groups']
        extra_kwargs = {
                            'contacts': {'required': False},
                            'blockeds': {'required': False},
                            'groups': {'required': False}
                        }
    contacts = serializers.PrimaryKeyRelatedField(queryset=models.ChatUser.objects.all(),
                                            required=True,
                                            allow_null=False,
                                            pk_field=serializers.UUIDField(format='hex_verbose'))



# restrain group to users groups
from uuid import uuid4
class ChatMessageSerializer(BaseSerializer):
    class Meta:
        model = models.ChatMessage
        fields = ['id', 'author', 'group', 'date', 'respond_to', 'body']
        extra_kwargs = {
            'date': {'format' : '%Y-%m-%dT%H:%M:%S.%fZ%z', 'default':timezone.now},
            'id': {'format' : 'hex_verbose', 'default': uuid4}
            }

    author = UserRelatedField(queryset=models.ChatUser.objects.all(), required=False)
    group = serializers.PrimaryKeyRelatedField(queryset=models.ChatGroup.objects.all(),
                                            required=True,
                                            allow_null=False,
                                            pk_field=serializers.UUIDField(format='hex_verbose'))



class ChatGroupSerializer(BaseSerializer):
    class Meta:
        model = models.ChatGroup
        fields = ['id', 'name', 'members', 'messages']

    members = UserRelatedField(queryset=models.ChatUser.objects.all(), many=True)
    messages = ChatMessageSerializer(many=True, required=False, fields='id author date body')


class ContactEventSerializer(serializers.Serializer):
    author = serializers.CharField(required=False)
    name = serializers.CharField()
    rel = serializers.CharField(required=False)#change to choice
    status = serializers.CharField(required=False)#change to choice

    def create(self, data):
        pass


class EventSerializer(serializers.Serializer):
    name = serializers.CharField()



content = b'{"id":"08c5e0ae-69b8-418e-84c5-9010ef8d1d1e","name":"luciole"}'
new = b'{"id":"62e661f9-a68e-4558-b833-339a90cecd01", "name":"xueyi"}'
