


from django.http import HttpResponse
from rest_framework.views import APIView

class LogoutRequest(APIView):
    def post(self, request):
        response = HttpResponse("Logged out successfully")
        response.delete_cookie('access', path='/')
        response.delete_cookie('refresh', path='/')
        return response

	
# class CustomPasswordResetConfirmView(PasswordResetConfirmView):
# 	template_name = 'password_reset_confirm.html'
# 	def form_valid(self, form):
# 		response = super().form_valid(form)
# 		return HttpResponse('Le mot de passe a ete modifier avec succes',  status=200)

# class PasswordRequestReset(APIView):
# 	def post(self, request):
# 		email = request.data.get('email')
# 		if not email:
# 			return Response({"error": "L'adresse email est requise."}, status=status.HTTP_400_BAD_REQUEST)
# 		try:
# 			user = CustomUser.objects.get(email = email)
# 			reset_url = GenerateVerificationUrl(request, user, 'password_reset_confirm')
# 			send_mail(
# 				'Réinitialisation mot de passe',
# 				f'Veuillez cliquer sur le lien pour réinitialiser votre mot de passe : {reset_url}',
# 				'jill.transcendance@gmail.com',
# 				[user.email],
# 				fail_silently=False,
# 			)
# 			return Response({"success": "Le lien de réinitialisaition de mot de passe à été envoyé avec succès."}, status=status.HTTP_200_OK)
# 		except CustomUser.DoesNotExist:
# 			return Response({"error": "L'adresse email est introuvable."}, status=status.HTTP_400_BAD_REQUEST)
		
# from rest_framework_simplejwt.tokens import RefreshToken

