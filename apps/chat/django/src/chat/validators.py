#chat/validators.py
from django.core.exceptions import ValidationError



def validate_futur(value):
	from django.utils import timezone

	now = timezone.now()
	if value > now:
		print(f'value : {value}')
		print(f'now : {now}')
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

def is_uuid(val):
    from uuid import UUID
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False

# validate date message :
    # - no futur date
    # - timeline coherence ? message cant be older than previous one
# validate author (at higher level)
# validate conv (at higher level)
# validate body length (at higher level)