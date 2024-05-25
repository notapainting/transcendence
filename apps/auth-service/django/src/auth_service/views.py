from tokenize import TokenError
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
from rest_framework_simplejwt.tokens import AccessToken
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
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import redirect

User = get_user_model()

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

class LogoutRequest(APIView):
    def post(self, request):
        response = HttpResponse("Logged out successfully")
        response.delete_cookie('access', path='/')  # Supprimer le cookie d'accès
        response.delete_cookie('refresh', path='/')  # Supprimer le cookie de rafraîchissement
        return response


class GetUserPersonnalInfos(APIView):
	authentication_classes = [JWTAuthentication]
	def get(self, request):
		access_token_cookie = request.COOKIES.get('access')
		user = get_user_from_access_token(access_token_cookie)
		user_data = {'username':user.username}
		response = requests.post('http://user-managment:8000/getuserinfo/', json=user_data)
		if response.status_code == 200:
			user_info = response.json()
			return Response(user_info, status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomTokenObtainPairView(TokenObtainPairView):
	serializer_class = CustomTokenObtainPairSerializer
	def post(self, request, *args, **kwargs):
		# Appeler la méthode post de la classe parent pour obtenir la réponse
		response = super().post(request, *args, **kwargs)
		# Récupérer les jetons d'accès et de rafraîchissement
		access_token = response.data.get('access')
		refresh_token = response.data.get('refresh')
		response.data.pop('access', None)
		response.data.pop('refresh', None)
		# Ajouter les cookies à la réponse
		response.set_cookie(key='access', value=access_token, httponly=True)
		response.set_cookie(key='refresh', value=refresh_token, httponly=True)
		return response

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
		
		# Vérifier si profile_picture n'est pas vide avant de l'ajouter à user_data
		if user.profile_picture:
			user_data['profile_picture'] = user.profile_picture
		response = requests.post('http://user-managment:8000/signup/', json=user_data)
		if (response.status_code == status.HTTP_201_CREATED):
			return HttpResponse('Lien de vérification valide', status=200)
		else:
			return HttpResponse("Erreur while creating user in user_managment service", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

class ValidateTokenView(APIView):
	authentication_classes = [JWTAuthentication]
	def post(self, request):
		access_token_cookie = request.COOKIES.get('access')
		user = get_user_from_access_token(access_token_cookie)
		return Response({'message': 'token valide.', 'username': user.username}, status=status.HTTP_200_OK)

from requests.exceptions import HTTPError

class UpdateProfilePicture(APIView):
	authentication_classes = [JWTAuthentication]
	def put(self, request, *args, **kwargs):
		access_token_cookie = request.COOKIES.get('access')
		user = get_user_from_access_token(access_token_cookie)
		profile_picture = request.FILES.get('profile_picture')
		if profile_picture:
			try:
				files = {'profile_picture': profile_picture}
				data = {'unique_id': user.unique_id}
				update_response = requests.put('http://user-managment:8000/update_client/', files=files, data=data)
				update_response.raise_for_status()
			except requests.exceptions.RequestException as e:
				return Response({"error": f"Failed to update user information: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			return Response({"message": "Profile picture updated successfully"}, status=status.HTTP_200_OK)
		else:
			return Response({"error": "No profile picture provided"}, status=status.HTTP_400_BAD_REQUEST)

class UpdateClientInfo(APIView):
	authentication_classes = [JWTAuthentication]
	def put(self, request, *args, **kwargs):
		access_token_cookie = request.COOKIES.get('access')
		user = get_user_from_access_token(access_token_cookie)
		try:
			request.data['unique_id'] = user.unique_id
			update_response = requests.put('http://user-managment:8000/update_client/', json=request.data)
			update_response.raise_for_status()  
		except requests.exceptions.RequestException as e:
			return Response({"error": f"Failed to update user information: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		data = request.data
		for key, value in data.items():
			if hasattr(user, key):
				setattr(user, key, value)
		user.save()
		return Response({"message": "User information updated successfully"}, status=status.HTTP_200_OK)

	
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
				'Réinitialisation mot de passe',
				f'Veuillez cliquer sur le lien pour réinitialiser votre mot de passe : {reset_url}',
				'jill.transcendance@gmail.com',
				[user.email],
				fail_silently=False,
			)
			return Response({"success": "Le lien de réinitialisaition de mot de passe à été envoyé avec succès."}, status=status.HTTP_200_OK)
		except CustomUser.DoesNotExist:
			return Response({"error": "L'adresse email est introuvable."}, status=status.HTTP_400_BAD_REQUEST)
		
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenRefreshView(TokenRefreshView):
	def post(self, request, *args, **kwargs):
		refresh_token_cookie = request.COOKIES.get('refresh')
		if not refresh_token_cookie:
			return Response({'error': 'Refresh token cookie not found'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			refresh_token = RefreshToken(refresh_token_cookie)
			access_token = refresh_token.access_token
			response = Response(status=status.HTTP_200_OK)
			response.set_cookie('access', str(access_token), httponly=True)  # Définition du cookie HTTPOnly
			return response
		except Exception as e:
			return Response({'error': 'Failed to refresh access token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import os
from django.http import JsonResponse

def authenticate_with_42(request):
	uid = os.getenv('UID')
	if uid is None:
		pass #implementer uen redirection
	authorization_url = f"https://api.intra.42.fr/oauth/authorize?client_id={uid}&redirect_uri=https://10.14.3.2:8443/auth/Oauth/&response_type=code"
	response = JsonResponse({'authorization_url': authorization_url})
	response["Access-Control-Allow-Origin"] = "*"
	response["Access-Control-Allow-Methods"] = "GET"
	response["Access-Control-Allow-Headers"] = "Content-Type"
	return response


import random
import string
from django.http import HttpResponseRedirect
def oauth_callback(request):
	code = request.GET['code']
	if code:
		token_url = "https://api.intra.42.fr/oauth/token"
		client_id = os.getenv('UID')
		client_secret = os.getenv('SECRET_KEY')
		redirect_url = "https://10.14.3.2:8443/auth/Oauth/"
		payload = {
			"grant_type": "authorization_code",
			"client_id": client_id,
			"client_secret": client_secret,
			"redirect_uri": redirect_url,
			"code": code
		}
		response = requests.post(token_url, data=payload)
		if response.ok:
			# Extraire le jeton d'accès de la réponse
			access_token = response.json().get('access_token')
			user_info_url = "https://api.intra.42.fr/v2/me"
			headers = {
				"Authorization": f"Bearer {access_token}"
			}
			user_info_response = requests.get(user_info_url, headers=headers)
			if user_info_response.ok :
				user_data = user_info_response.json()	
				password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
				username = user_data.get('login')
				profile_picture = user_data.get('image', {}).get('versions', {}).get('small')
				print(profile_picture)
				email = user_data.get('email')
				if CustomUser.objects.filter(username=username).exists() and CustomUser.objects.filter(is_42=False).exists():
					pass #implementer une feature de username set si deja pris par un compte non 42.
				elif not CustomUser.objects.filter(username=username).exists():
					serializer = UserSerializer(data={
					'username': username,
					'password': password,
					'email': email,
					'is_42': True,
					'profile_picture': profile_picture
					})
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
				return redirect('https://localhost:8443/?username={}&profile_picture={}&email={}'.format(username, profile_picture, email))
				return JsonResponse({'username': username, 'profile_picture': profile_picture, 'email': email, 'password': password})
			else:	
				return JsonResponse({'error': 'Échec de la récuperation des informatiosn utilisateur'}, status=400)
		else:
			return JsonResponse({'error': 'Échec de la récupération du jeton d\'accès'}, status=400)
	else:
		return JsonResponse({'error': 'Code d\'autorisation manquant dans la requête'}, status=400)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

import pyotp
import qrcode
import base64
from io import BytesIO

class Activate2FAView(APIView):
	authentication_classes = [JWTAuthentication]

	def generate_qr_code(self, secret_key, otp_url):
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data(otp_url)
		qr.make(fit=True)
		qr_img = qr.make_image(fill_color="black", back_color="white")
		buffer = BytesIO()
		qr_img.save(buffer, "PNG")
		qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
		return qr_base64

	def post(self, request):
		# Génération de la clé secrète pour l'utilisateur
  
		access_token_cookie = request.COOKIES.get('access')
		user = get_user_from_access_token(access_token_cookie)
		secret_key = pyotp.random_base32()
		
		# Génération de l'URL pour le QR code
		otp_url = pyotp.totp.TOTP(secret_key).provisioning_uri(user.email, issuer_name="Nom de votre application")

		# Générer le QR code en base64
		qr_base64 = self.generate_qr_code(secret_key, otp_url)

		# Activer la 2FA pour l'utilisateur
		user.secret_key = secret_key
		user.save()

		return Response({'qr_img': qr_base64, 'secret_key': secret_key}, status=status.HTTP_200_OK)


class Confirm2FAView(APIView):
	authentication_classes = [JWTAuthentication]
	def post(self, request):
		access_token_cookie = request.COOKIES.get('access')
		user = get_user_from_access_token(access_token_cookie)
		print("salut")
		if request.method == 'POST':
			code = request.data.get('code')
			print(code)
			secret_key = user.secret_key
			if pyotp.TOTP(secret_key).verify(code):
				user.is_2fa_enabled = True
				user.save()
				return Response({'success': True})
			else:
				return Response({'success': False, 'error': 'Code incorrect'}, status=status.HTTP_400_BAD_REQUEST)

		return Response({'error': 'Méthode non autorisée'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)