from urllib.parse import urlparse, urlunparse
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_service.serializers import UserSerializer
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.throttling import AnonRateThrottle
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from auth_service.models import CustomUser
from django.urls import reverse
from django.http import HttpResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetConfirmView
from django.shortcuts import render
from django.views.generic import View


User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		data = super().validate(attrs)
		user = self.user
		if not user.isVerified:
			raise AuthenticationFailed('Email non vérifié.')
		user_data = {'username':user.username}
		response = requests.post('http://user-managment:8000/getuserinfo/', json=user_data)
		if response.status_code == 200:
			user_info = response.json()
			data.update(user_info)
		return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

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
				'email' : user.email
		}
		response = requests.post('http://user-managment:8000/signup/', json=user_data)
		if (response.status_code == status.HTTP_201_CREATED):
			return HttpResponse('Lien de vérification valide', status=200)
		else:
			return Response("Erreur while creating user in user_managment service", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	else:
		return HttpResponse('Lien de vérification invalide ou expiré', status=400)

def GenerateVerificationUrl(request, user, viewname):
	token = default_token_generator.make_token(user)
	uid = urlsafe_base64_encode(force_bytes(user.pk))
	path = reverse(viewname, kwargs={'uidb64': uid, 'token': token})
	verification_url = request.build_absolute_uri(path)
     
	#pour le port 8443 TEMPORAIRE
	if '8080' not in verification_url:
		parts = list(urlparse(verification_url))
		parts[1] = parts[1].replace('localhost', 'localhost:8080')  # Replace the domain part
		verification_url = urlunparse(parts)
	return verification_url

class UserCreate(APIView):
	def post(self, request):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()
			full_verification_url = GenerateVerificationUrl(request, user, 'verify_email')
			send_mail(
				'Vérifiez votre adresse email',
				f'olalaaaaa sa marche : {full_verification_url}',
				'jill.transcendance@gmail.com',
				[user.email],
				fail_silently=False,
			)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
	template_name = 'password_reset_confirm.html'
	def form_valid(self, form):
		response = super().form_valid(form)
		return HttpResponse('Le mot de passe a ete modifier avec succes',  status=200)
     
class PasswordRequestReset(APIView):
	def post(self, request):
		email = request.data.get('email')
		if not email:
			return Response({"error": "L'adresse email est requise."}, status=status.HTTP_400_BAD_REQUEST)
		try:
			user = CustomUser.objects.get(email = email)
			reset_url = GenerateVerificationUrl(request, user, 'password_reset_confirm')
			send_mail(
				'Reinitialisation mot de passe',
				f'Veuillez cliquer sur le lien pour reinitialiser votre mot de passe : {reset_url}',
				'jill.transcendance@gmail.com',
				[user.email],
				fail_silently=False,
			)
			return Response({"success": "Le lien de réinitialisaition de mot de passe à été envoyé avec succès."}, status=status.HTTP_200_OK)
		except CustomUser.DoesNotExist:
			return Response({"error": "L'adresse email est introuvable."}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenRefreshView(TokenRefreshView):
    throttle_classes = (AnonRateThrottle,)