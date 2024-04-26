from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.validators import UniqueValidator

from . import models
import io

def parse_json(json_data):
	return JSONParser().parse(io.BytesIO(json_data))


def render_json(raw_data):
        return (JSONRenderer().render(raw_data)) 

class   BaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if hasattr(self, 'initial_data') is True and self.initial_data is not None:
            self.initial_data = self.parse_json()
        

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


class UserSerializer(BaseSerializer):
    
    class Meta:
        model = models.ChatUser
        fields = ['name', 'contact_list', 'blocked_list', 'groups']
        extra_kwargs = {
                            'contact_list': {'required': False},
                            'blocked_list': {'required': False},
                            'groups': {'required': False}
                        }

class UserRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        return models.ChatUser.objects.get(name=data)

class MessageSerializer(BaseSerializer):
    author = UserRelatedField(queryset=models.ChatUser.objects.all())

    class Meta:
        model = models.ChatMessage
        fields = ['id', 'author', 'group', 'date_pub', 'respond_to', 'body']
        extra_kwargs = {
                	'date_pub': {'required': False},
                	'respond_to': {'required': False}
                }

class GroupSerializer(BaseSerializer):
    members = UserRelatedField(queryset=models.ChatUser.objects.all(), many=True)
    messages = MessageSerializer(many=True, fields='id author body')

    class Meta:
        model = models.ChatGroup
        fields = ['id', 'name', 'members', 'messages']
        extra_kwargs = {
                	'messages': {'required': False}
                }



content = b'{"id":"08c5e0ae-69b8-418e-84c5-9010ef8d1d1e","name":"luciole"}'
new = b'{"id":"62e661f9-a68e-4558-b833-339a90cecd01", "name":"xueyi"}'
