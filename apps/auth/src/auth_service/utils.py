from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import urlparse, urlunparse
from auth_service.models import CustomUser

def get_user_from_access_token(access_token_cookie):
	try:
		token = AccessToken(access_token_cookie)
		user_id = token['user_id']
		user = CustomUser.objects.get(id=user_id)
		return user
	except CustomUser.DoesNotExist:
		raise AuthenticationFailed("User not found")
	except Exception as e:
		raise AuthenticationFailed("Error validating access token: {}".format(str(e)))
