from django.http import JsonResponse
from rest_framework.views import APIView
from user_managment.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from user_managment.models import CustomUser
import requests
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile


class UserCreate(APIView):
	def post(self, request):
		profile_picture_url = request.data.get('profile_picture', None)
		request.data.pop('profile_picture', None)
		serializer = UserSerializer(data = request.data)
		if serializer.is_valid():
			user = serializer.save()
			if profile_picture_url:
				response = requests.get(profile_picture_url)
				if response.ok:
					image_content = ContentFile(response.content)
					user.profile_picture.delete(save=False)
					user.profile_picture.save(f"{user.username}.jpg", image_content, save=True)
			user_data = serializer.data
			return Response(user_data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	# def update(self, request):

class UpdateClientInfo(APIView):
	def put(self, request, *args, **kwargs):
		try:
			user = CustomUser.objects.get(unique_id=request.data['unique_id'])
		except CustomUser.DoesNotExist:
			return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
		data = request.data
		for key, value in data.items():
			if key == 'profile_picture':
				# Si la clé est 'profile_picture'
				user.profile_picture.delete(save=False)
				user.profile_picture.save(f"{user.username}.jpg", value, save=True)
				return Response({"message": "User information updated successfully"}, status=status.HTTP_200_OK)
			if hasattr(user, key):
				setattr(user, key, value)
			user.save()
		return Response({"message": "User information updated successfully"}, status=status.HTTP_200_OK)

class GetUserInfos(APIView):
	def post(self, request):
		username = request.data.get('username', None)
		if username:
			try:
				user = CustomUser.objects.get(username = username)
				user_data = {
					'username': user.username,
                    'email': user.email,
                    'isVerified': user.isVerified,
                    'unique_id': user.unique_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_of_birth': user.date_of_birth,
                    'gender': user.gender,
					'profile_picture': user.profile_picture.url if user.profile_picture else None,
				}
				return Response(user_data, status = 200)
			except CustomUser.DoesNotExist:
				return Response("User not found", status=404)
		else:
			return Response("User not in request", status=404)

