#chat/validators.py
from django.core.exceptions import ValidationError



def validate_futur(value):
	from django.utils import timezone

	now = timezone.now()
	if value > now:
		raise ValidationError(
			"Message from futur",
			params={"value": value, 'current': now}
		)

def offensive_name(value):
	set = ['lapin', 'poulet']
	for name in set:
		if value == name:
			raise ValidationError(
				"Name is offensive",
				params={'value': value}
			)

