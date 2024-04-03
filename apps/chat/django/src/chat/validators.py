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
