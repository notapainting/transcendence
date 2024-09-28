from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from urllib.parse import urlparse, urlunparse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from auth_service.models import CustomUser
import requests
from rest_framework import status
from django.http import HttpResponse
import os

host = os.getenv('host')


def GenerateVerificationUrl(request, user, viewname):
	token = default_token_generator.make_token(user)
	uid = urlsafe_base64_encode(force_bytes(user.pk))
	path = reverse(viewname, kwargs={'uidb64': uid, 'token': token})
	verification_url = request.build_absolute_uri(path)
     
	#pour le port 8443 TEMPORAIRE
	if '8443' not in verification_url:
		parts = list(urlparse(verification_url))
		parts[1] = parts[1].replace(f"{host}", f"{host}:8443") 
		verification_url = urlunparse(parts)
	return verification_url

def send_verification_email(email, verification_url):
	subject = 'Confirm Your Transcendence Account'
	message = f"""
	Hello,

	Thank you for registering on Transcendence! We're excited to have you join our community. Before you can start using your account, we need to verify your email address. Please click the link below to confirm your account:

	{verification_url}

	If you are unable to click the link, you can copy and paste it into your browser's address bar.

	If you did not register for an account on Transcendence, please ignore this email.

	Best regards,
	The Transcendence Team
	"""
	send_mail(
		subject,
		message,
		'jill.transcendance@gmail.com',
		[email],
		fail_silently=False,
	)

def verify_email(request, uidb64, token):
	try:
		uid = urlsafe_base64_decode(uidb64).decode('utf-8')
		user = CustomUser.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
		user = None
	if user is not None and default_token_generator.check_token(user, token):
		user.isVerified = True
		user.save()
		user_data = {
			'username': user.username,
			'email': user.email,
			'unique_id': user.unique_id
		}
		if user.profile_picture:
			user_data['profile_picture'] = user.profile_picture
		response = requests.post('http://user:8000/signup/', json=user_data, verify=False)
		if (response.status_code == status.HTTP_201_CREATED):
			return HttpResponse('Lien de vérification valide', status=200)
		else:
			return HttpResponse("Erreur while creating user in user_managment service", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	else:
		return HttpResponse('Lien de vérification invalide ou expiré', status=400)