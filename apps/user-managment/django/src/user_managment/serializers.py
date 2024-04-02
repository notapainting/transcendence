from user_managment.models import CustomUser
from django.contrib.auth.hashers import make_password
import uuid

	
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
	#modification de la classe parent ici ModelSerializer en lui fournissant certaines données
	class Meta: 
		#spécifie que le serializer va manipuler les Users
		model = CustomUser
		#specifie quels champs il va manipuler
		fields = ['id', 'username', 'email', 'isVerified', 'profile_picture', 'first_name', 'last_name', 'date_of_birth', 'gender']
	def create(self, validated_data):
		return CustomUser.objects.create(**validated_data)
	def update(self, instance, validated_data):
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		instance.save()
		return instance