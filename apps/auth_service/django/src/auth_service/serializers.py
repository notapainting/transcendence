
from django.contrib.auth.models import User
from auth_service.models import CustomUser
	
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
	def create(self, validated_data): #post
		user = CustomUser.objects.create_user(
			username = validated_data['username'],
			email = validated_data['email'],
		)
		user.set_password(validated_data['password'])
		user.save()
		return user
	def update(self, instance, validated_data): #put ou patch
		instance.email = validated_data.get('email', instance.email)
		instance.set_password(validated_data['password'])
		instance.save()
		return instance