from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
import pyotp
import requests
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from auth_service.utils import get_user_from_access_token


class ValidateTokenView(APIView):
	authentication_classes = [JWTAuthentication]
	def post(self, request):
		access_token_cookie = request.COOKIES.get('access')
		user = get_user_from_access_token(access_token_cookie)
		return Response({'message': 'token valide.', 'username': user.username}, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView):
	def post(self, request, *args, **kwargs):
		refresh_token_cookie = request.COOKIES.get('refresh')
		if not refresh_token_cookie:
			return Response({'error': 'Refresh token cookie not found'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			refresh_token = RefreshToken(refresh_token_cookie)
			access_token = refresh_token.access_token
			user_id = access_token['user_id']
			user = User.objects.get(id=user_id)
			username = user.username

			response = Response({'username': username}, status=status.HTTP_200_OK)
			response.set_cookie('access', str(access_token), httponly=True, secure=True)
			return response
		except Exception as e:
			return Response({'error': 'Failed to refresh access token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		username_or_email = attrs.get('username')
		password = attrs.get('password')
		user = authenticate(username=username_or_email, password=password)
		if user is None:
			try:
				user = User.objects.get(email=username_or_email)
				if not user.check_password(password):
					raise AuthenticationFailed('No active account found with the given credentials')
			except User.DoesNotExist:
				raise AuthenticationFailed('No active account found with the given credentials')
		if not user.is_active:
			raise AuthenticationFailed('No active account found with the given credentials')
		if not user.isVerified:
			raise AuthenticationFailed('Email not verified.')
		if user.is_2fa_enabled:
			code = self.context['request'].data.get('code')
			if not code:
				raise AuthenticationFailed('Two Factor Authentification needed.')
			secret_key = user.secret_key
			if not pyotp.TOTP(secret_key).verify(code):
				raise AuthenticationFailed('Incorrect 2FA code. Please try again.', code='invalid_2fa_code')
		refresh = self.get_token(user)
		data = {
			'refresh': str(refresh),
			'access': str(refresh.access_token),
		}
		user_data = {'username': user.username}
		response = requests.post('http://user:8000/getuserinfo/', json=user_data, verify=False)
		if response.status_code == 200:
			user_info = response.json()
			data.update(user_info)
		return data


class CustomTokenObtainPairView(TokenObtainPairView):
	serializer_class = CustomTokenObtainPairSerializer
	def post(self, request, *args, **kwargs):
		try:
			response = super().post(request, *args, **kwargs)
			access_token = response.data.get('access')
			refresh_token = response.data.get('refresh')
			response.data.pop('access', None)
			response.data.pop('refresh', None)

			response.set_cookie(key='access', value=access_token, httponly=True, secure=True)
			response.set_cookie(key='refresh', value=refresh_token, httponly=True, secure=True)
			return response
		except AuthenticationFailed as e:
			return Response(e.detail, status=status.HTTP_403_FORBIDDEN)