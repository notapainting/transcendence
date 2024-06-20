from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from auth_service.utils import get_user_from_access_token

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
				update_response = requests.put('http://user-managment:8000/update_client/', files=files, data=data, verify=False)
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
		print(user.unique_id)
		try:
			request.data['unique_id'] = user.unique_id
			update_response = requests.put('http://user-managment:8000/update_client/', json=request.data, verify=False)
			update_response.raise_for_status()  
		except requests.exceptions.RequestException as e:
			return Response({"error": f"Failed to update user information: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		data = request.data
		for key, value in data.items():
			if hasattr(user, key):
				setattr(user, key, value)
		user.save()
		return Response({"message": "User information updated successfully"}, status=status.HTTP_200_OK)


class GetUserPersonnalInfos(APIView):
	authentication_classes = [JWTAuthentication]
	def get(self, request):
		access_token_cookie = request.COOKIES.get('access')
		user = get_user_from_access_token(access_token_cookie)
		user_data = {'username':user.username}
		response = requests.post('http://user-managment:8000/getuserinfo/', json=user_data, verify=False)
		if response.status_code == 200:
			user_info = response.json()
			user_info['is_2fa_enabled'] = user.is_2fa_enabled
			return Response(user_info, status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)