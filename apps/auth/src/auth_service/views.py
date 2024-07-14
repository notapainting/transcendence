


from django.http import HttpResponse
from rest_framework.views import APIView

class LogoutRequest(APIView):
    def post(self, request):
        response = HttpResponse("Logged out successfully")
        response.delete_cookie('access', path='/')
        response.delete_cookie('refresh', path='/')
        return response