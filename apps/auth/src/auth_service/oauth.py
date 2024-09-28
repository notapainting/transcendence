from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import get_user_model
import requests
import random
import string
from rest_framework_simplejwt.tokens import RefreshToken
from auth_service.models import CustomUser
import os
import uuid

host = os.getenv('HOST');

def authenticate_with_42(request):
	uid = os.getenv('UID')
	if uid is None:
		pass #implementer uen redirection
	authorization_url = f"https://api.intra.42.fr/oauth/authorize?client_id={uid}&redirect_uri=https://{host}:8443/auth/Oauth/&response_type=code"
	response = JsonResponse({'authorization_url': authorization_url})
	response["Access-Control-Allow-Origin"] = "*"
	response["Access-Control-Allow-Methods"] = "GET"
	response["Access-Control-Allow-Headers"] = "Content-Type"
	return response

def oauth_callback(request):
	code = request.GET.get('code')
	if code:
		token_url = "https://api.intra.42.fr/oauth/token"
		client_id = os.getenv('UID')
		client_secret = os.getenv('SECRET_KEY')
		redirect_url = "https://{host}:8443/auth/Oauth/"
		payload = {
			"grant_type": "authorization_code",
			"client_id": client_id,
			"client_secret": client_secret,
			"redirect_uri": redirect_url,
			"code": code
		}
		response = requests.post(token_url, data=payload)
		if response.ok:
			access_token = response.json().get('access_token')
			user_info_url = "https://api.intra.42.fr/v2/me"
			headers = {"Authorization": f"Bearer {access_token}"}
			user_info_response = requests.get(user_info_url, headers=headers)
			if user_info_response.ok:
				user_data = user_info_response.json()
				oauth_id = user_data['id']
				username = user_data.get('login')
				email = user_data.get('email')
				profile_picture = user_data.get('image', {}).get('versions', {}).get('medium')

				original_username = username
				counter = 1
				while CustomUser.objects.filter(username=username).exists():
					username = f"{original_username}{counter}"
					counter += 1
				user, created = CustomUser.objects.get_or_create(
					oauth_id=oauth_id,
					defaults={
						'username': username,
						'email': email,
						'profile_picture': profile_picture,
						'password': ''.join(random.choices(string.ascii_letters + string.digits, k=12)),
						'is_42': True,
						'unique_id': str(uuid.uuid4()),
					}
				)
				if created:
					account = {
						'username': username,
						'email': user.email,
						'profile_picture': profile_picture,
						'unique_id': user.unique_id
					}
					requests.post('http://user:8000/signup/', json=account, verify=False)
				refresh = RefreshToken.for_user(user)
				access_token_jwt = str(refresh.access_token)
				response = HttpResponseRedirect('https://{host}:8443/')
				response.set_cookie('access', access_token_jwt, httponly=True, secure=True, samesite='Lax')
				response.set_cookie('refresh', str(refresh), httponly=True, secure=True, samesite='Lax')
				return response
			else:
				return JsonResponse({'error': 'Échec de la récupération des informations utilisateur'}, status=400)
		else:
			return JsonResponse({'error': 'Échec de la récupération du jeton d\'accès'}, status=400)
	else:
		return JsonResponse({'error': 'Code d\'autorisation manquant dans la requête'}, status=400)