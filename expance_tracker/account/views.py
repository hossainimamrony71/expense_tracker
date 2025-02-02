from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token 
from rest_framework import status
from .serializers import UserSerializer 
from .models import User 
from .permissions import IsAdmin

class CustomAuthToken(ObtainAuthToken):
    def post (self, requsts, *args, **kwargs):
        response = super(CustomAuthToken, self).post(requsts, *args, **kwargs)
        token = Token.objects.get(key = response.data['token'])
        return Response({"token": token.key, "user_id": token.user_id})


@api_view(["POST"])
@permission_classes([IsAdmin])
def creat_user(request, *args, **kwargs):
    serializer = UserSerializer(data = request.data)
    if serializer.is_valid():
        user = serializer.save()
        Token.objects.create(user = user)  #created token
        return Response(serializer.data, status= status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def change_pass(request, pk=None, *args, **kwargs):
    if pk:
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data = request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)