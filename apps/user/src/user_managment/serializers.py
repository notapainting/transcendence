from user_managment.models import CustomUser
from django.contrib.auth.hashers import make_password
import uuid

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

import user_managment.models as mod

from django.utils import timezone
def validate_date_of_birth(value):
    if value > timezone.now().date():
        raise ValidationError("Date of birth cannot be in the future.")

class UserSerializer(serializers.ModelSerializer):
	class Meta: 
		model = CustomUser
		fields = ['id', 'username', 'email', 'isVerified', 'unique_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'profile_picture']

	def validate(self, data):
		errors = {}

		if 'username' in data:
			username = data['username']
			if not username:
				errors['username'] = "Username cannot be empty."
			elif not username.isalnum():
				print("ERROR USERNAME")
				errors['username'] = "Username should contain only alphanumeric characters."
		
		if 'email' in data:
			email = data['email']
			if email:
				try:
					validate_email(email)
				except ValidationError:
					print("ERROR EMAIL")
					errors['email'] = "Invalid email format."

		if 'date_of_birth' in data:
			date_of_birth = data['date_of_birth']
			if date_of_birth:
				try:
					validate_date_of_birth(date_of_birth)
				except ValidationError as e:
					print("ERROR DATE OF BIRTH")
					errors['date_of_birth'] = str(e)

		if 'gender' in data:
			gender = data['gender']
			if gender:
				if gender not in [choice[0] for choice in CustomUser.GENDER_CHOICES]:
					print("ERROR GENDER")
					errors['gender'] = "Invalid gender choice."

		if errors:
			raise serializers.ValidationError(errors)

		return data

	def update(self, instance, validated_data):
		for attr, value in validated_data.items():
			if attr == 'date_of_birth' and value == '':
				continue
			if attr == 'profile_picture':
				continue
			setattr(instance, attr, value)
		instance.save()
		return instance


# fields
class UserRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance
    def to_representation(self, value):
        return str(value)
    def to_internal_value(self, data):
        try :
            return mod.CustomUser.objects.get(username=data)
        except ObjectDoesNotExist:
            raise ValidationError({'User': 'User not found'})

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = mod.Match
        fields = ['winner', 'loser', 'score_w', 'score_l', 'date']
    
    winner = UserRelatedField(queryset=mod.CustomUser.objects.all())
    loser = UserRelatedField(queryset=mod.CustomUser.objects.all())

