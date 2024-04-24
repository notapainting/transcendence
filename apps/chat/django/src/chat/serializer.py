from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from . import models
import io


class   BaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if self.instance is None and self.initial_data is not None:
            self.initial_data = self.parse_json()
        
        # Drop any fields that are not specified in the `fields` argument.
        if fields is not None:
            if isinstance(fields, basestring): #types.StringTypes
                allowed = fields
            else:
                allowed = set(fields)
            print(allowed)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def parse_json(self):
        return JSONParser().parse(io.BytesIO(self.initial_data))


    def render_json(self):
        return (JSONRenderer().render(self.data)) 


class ChatUserSerializer(BaseSerializer):
    id = serializers.UUIDField()
    
    class Meta:
        model = models.ChatUser
        fields = ['id', 'name', 'contact_list', 'blocked_list', 'groups']
        extra_kwargs = {
                            'contact_list': {'required': False},
                            'blocked_list': {'required': False},
                            'groups': {'required': False}
                        }


content = b'{"id":"08c5e0ae-69b8-418e-84c5-9010ef8d1d1e","name":"luciole"}'
new = b'{"id":"62e661f9-a68e-4558-b833-339a90cecd01", "name":"xueyi"}'