from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

import qrcode
from io import BytesIO
import base64
import pyotp

from auth_service.models import CustomUser
from auth_service.utils import get_user_from_access_token

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
		access_token_cookie = request.COOKIES.get('access')
		user = get_user_from_access_token(access_token_cookie)
		if user.is_2fa_enabled:
			return Response({"error": "Two Factor Authentication is already enabled for this user."}, status=status.HTTP_400_BAD_REQUEST)
		secret_key = pyotp.random_base32()
		
		otp_url = pyotp.totp.TOTP(secret_key).provisioning_uri(user.email, issuer_name="Nom de votre application")

		qr_base64 = self.generate_qr_code(secret_key, otp_url)

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