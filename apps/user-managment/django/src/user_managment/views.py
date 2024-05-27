from django.http import JsonResponse
from rest_framework.views import APIView
from user_managment.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from user_managment.models import CustomUser
import requests
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from user_managment.matchs import MatchResults


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

from rest_framework.parsers import JSONParser
from io import BytesIO
from .serializers import MatchSerializer

# Json's model send by the game:
#   {
#     "host":"host's name", 
#     "host_score":"host's score", 
#     "host_powerups":"host's number of powerups", 
#     "client":"client's name", 
#     "client_score":"client's score",
#     "client_powerups":"client's number of powerups",
#     "match_start":"2024-05-21T11:01:44.496921Z"
#   }

def parse_json(data):
    return JSONParser().parse(BytesIO(data))

class MatchsInfos(APIView):
    def post(self, request):
            data = JSONParser().parse(request)

            # Find the Users in the DB from the str given in the json
            try:
                u1 = CustomUser.objects.get(username=data["host"])
                data['host_name'] = data['host']
                data['host'] = u1.id
            except:
                return Response("User_one not found", status=404)

            try:
                u2 = CustomUser.objects.get(username=data["client"])
                data['client_name'] = data['client']
                data['client'] = u2.id
            except:
                return Response("User_two not found", status=404)

            # Serialize the information for the storage of the match's info in the DB
            new_match = MatchSerializer(data=data)
            if new_match.is_valid():
                new_match.save()
                return Response("Match saved", status=200)

            return Response("POST: Something went wrong =(", status=500)

    def get(self, request):
        try:
            all_match = MatchResults.objects.all()
            serializer = MatchSerializer(all_match, many=True)
            return Response(serializer.data, status=200)
        except:
            return Response("GET: Something went wrong =(", status=500)

class UserMatchsInfos(APIView):
    def get(self, request, **args):
        name = args.get('name', None)

        # Search the username given in the url in the MatchResults' DB
        user_matchs = MatchResults.objects.filter(host_name=name) | MatchResults.objects.filter(client_name=name)
        serialzer = MatchSerializer(user_matchs, many=True)
        return Response(serialzer.data, status=200)
        