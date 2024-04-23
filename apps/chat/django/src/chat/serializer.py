from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from . import models
import io



class ChatUserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    
    class Meta:
        model = models.ChatUser
        fields = ['id', 'name', 'contact_list', 'blocked_list', 'groups']
        extra_kwargs = {
            				'contact_list': {'required': False},
                       		'blocked_list': {'required': False}
                        }
        

def parse(raw):
	return JSONParser().parse(io.BytesIO(raw))

content = b'{"id":"08c5e0ae-69b8-418e-84c5-9010ef8d1d1e","name":"luciole"}'

def render(data):
	return (JSONRenderer().render(data))
