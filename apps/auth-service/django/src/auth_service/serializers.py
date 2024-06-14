
from django.contrib.auth.models import User
from auth_service.models import CustomUser
from django.contrib.auth.hashers import make_password
import uuid

from rest_framework import serializers

from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.validators import UniqueValidator, ValidationError
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
	username = serializers.CharField(
		validators=[UnicodeUsernameValidator()],
		required=True,
		max_length=150,
		min_length=1,
		help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
	)
	email = serializers.EmailField(
		validators=[UniqueValidator(queryset=CustomUser.objects.all())],
		required=True,
		max_length=255,
		help_text='Required. Valid email address.'
	)

	password = serializers.CharField(
		write_only=True,
		required=True,
		help_text='Required. Password must be at least 8 characters long and contain a combination of letters, numbers, and special characters.'
	)

	class Meta:
		model = CustomUser
		fields = ['id', 'username', 'email', 'password', 'is_42', 'profile_picture']
		extra_kwargs = {'password': {'write_only': True, 'required': True}}

	def create(self, validated_data):
		unique_id = str(uuid.uuid4())
		validated_data['password'] = make_password(validated_data['password'])
		validated_data['unique_id'] = unique_id
		return CustomUser.objects.create(**validated_data)

	def validate_password(self, value):
		validate_password(value)
		return value

	def validate(self, data):
		username = data.get('username')
		email = data.get('email')
		if CustomUser.objects.filter(username=username).exists():
			raise ValidationError({'username': 'This username is already in use.'})
		if CustomUser.objects.filter(email=email).exists():
			raise ValidationError({'email': 'This email address is already in use.'})
		password = data.get('password')
		if password:
			validate_password(password)
		return data