from django.http import JsonResponse
from rest_framework.views import APIView
from user_managment.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from user_managment.models import CustomUser

class UserCreate(APIView):
	def post(self, request):
		serializer = UserSerializer(data = request.data)
		if serializer.is_valid():
			user = serializer.save()
			user_data = serializer.data
			return Response(user_data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetUserInfos(APIView):
	def post(self, request):
		username = request.data.get('username', None)
		if username:
			try:
				user = CustomUser.objects.get(username = username)
				serializer = UserSerializer(user)
				return Response(serializer.data, status = 200)
			except CustomUser.DoesNotExist:
				return Response("User not found", status=404)
		else:
			return Response("User not in request", status=404)