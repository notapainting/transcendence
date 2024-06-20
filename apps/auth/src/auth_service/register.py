from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_service.serializers import UserSerializer
from auth_service.mailing import GenerateVerificationUrl, send_verification_email

class UserCreate(APIView):
	def post(self, request):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()
			full_verification_url = GenerateVerificationUrl(request, user, 'verify_email')
			send_verification_email(user.email, full_verification_url)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
