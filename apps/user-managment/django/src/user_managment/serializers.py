from user_managment.models import CustomUser
from django.contrib.auth.hashers import make_password
import uuid
from .matchs import MatchResults

	
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
	#modification de la classe parent ici ModelSerializer en lui fournissant certaines données
	class Meta: 
		#spécifie que le serializer va manipuler les Users
		model = CustomUser
		#specifie quels champs il va manipuler
		fields = ['id', 'username', 'email', 'isVerified', 'unique_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'profile_picture']
	def create(self, validated_data):
		return CustomUser.objects.create(**validated_data)
	def update(self, instance, validated_data):
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		instance.save()
		return instance

from django.core.exceptions import ObjectDoesNotExist
from  user_managment.models import CustomUser

class UserMatchRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return str(value)
    def to_internal_value(self, data):
        try :
            return CustomUser.objects.get(username=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'User': 'User not found'})

class MatchSerializer(serializers.ModelSerializer):
	class Meta:
		model = MatchResults
		fields = ['user_one', 'user_one_name', 'user_one_score', 'user_one_powerups','user_two', 'user_two_name', 'user_two_score', 'user_two_powerups', 'match_start', 'match_end']

		user_one = UserMatchRelatedField(queryset=CustomUser.objects.all())
		# user_two = UserRelatedField(queryset=CustomUser.objects.all())