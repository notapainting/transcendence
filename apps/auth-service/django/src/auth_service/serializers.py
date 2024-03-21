
from django.contrib.auth.models import User
from auth_service.models import CustomUser
from django.contrib.auth.hashers import make_password
import uuid

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
	#modification de la classe parent ici ModelSerializer en lui fournissant certaines données
	class Meta: 
		#spécifie que le serializer va manipuler les Users
		model = CustomUser
		#specifie quels champs il va manipuler
		fields = ['id', 'username', 'email', 'password'] 
		#definir des comportements supplementaire pour certain champs (write only - impossible de renvoyer le champ password au client)
		extra_kwargs = {'password' : {'write_only' :True , 'required': True}} 
		#surcharge
	def create(self, validated_data):
		verification_key = str(uuid.uuid4())
		validated_data['password'] = make_password(validated_data['password'])
		validated_data['verification_key'] = verification_key
		return CustomUser.objects.create(**validated_data)