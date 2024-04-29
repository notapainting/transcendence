from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.serializers import ValidationError
from . import models
import io
from uuid import uuid4

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
        try :
            return models.ChatUser.objects.get(name=data)
        except BaseException:
            raise ValidationError({'ChatUser': 'User not found'})

# serializer
class   BaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            fields = fields.split()
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)



class ChatUser(BaseSerializer):
    class Meta:
        model = models.ChatUser
        fields = ['name', 'contacts', 'blockeds', 'groups']
        extra_kwargs = {
                            'contacts': {'required': False},
                            'blockeds': {'required': False},
                            'groups': {'required': False}
                        }
    contacts = UserRelatedField(queryset=models.ChatUser.objects.all(), many=True, required=False)
    
    # contacts = serializers.PrimaryKeyRelatedField(queryset=models.ChatUser.objects.all(),
    #                                         required=True,
    #                                         allow_null=False,
    #                                         pk_field=serializers.UUIDField(format='hex_verbose'))


# restrain group to users groups
class ChatMessage(BaseSerializer):
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


class ChatGroup(BaseSerializer):
    class Meta:
        model = models.ChatGroup
        fields = ['id', 'name', 'members', 'messages']

    members = UserRelatedField(queryset=models.ChatUser.objects.all(), many=True)
    messages = ChatMessage(many=True, required=False, fields='id author date body')


# event serializer
class EventBaseSerializer(serializers.Serializer):
    author = serializers.CharField(required=False)

    def create(self, data):
        print(self.validated_data)


class EventContact(EventBaseSerializer):
    name = UserRelatedField(queryset=models.ChatUser.objects.all())
    rel = serializers.CharField()#change to choice
    op = serializers.CharField()#change to choice


class EventStatus(EventBaseSerializer):
    status = serializers.CharField()#change to choice






content = b'{"id":"08c5e0ae-69b8-418e-84c5-9010ef8d1d1e","name":"luciole"}'
new = b'{"id":"62e661f9-a68e-4558-b833-339a90cecd01", "name":"xueyi"}'
