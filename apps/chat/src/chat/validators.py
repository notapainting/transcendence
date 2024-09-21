#chat/validators.py

from django.core.exceptions import ValidationError

def offensive_name(value):
	set = ['lapin', 'poulet']
	for name in set:
		if value == name:
			raise ValidationError(
				"Name is offensive",
				params={'value': value}
			)

def special_name(value):
	set = ['@']
	for name in set:
		if value == name:
			raise ValidationError(
				"Name is forbidden",
				params={'value': value}
			)

