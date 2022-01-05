from django.contrib.auth.models import User, Group
from django.http import response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from rest_framework.serializers import Serializer
from accounts.api.serializers import UserSerializer, LoginSerializer, SignupSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset =  User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes =  [permissions.IsAuthenticated]



class AccountViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    #serializer_class = SignupSerializer

    @action(methods = ['POST'], detail= False)
    def login(self, request):
        serializer = LoginSerializer(data =  request.data)
        if not serializers.is_valid():
            return Response({
                "success": False,
                "message" : "Please check input",
                "error": serializer.errors
            }, status = 400)
        username = serializer.validated_data['username']
        password =  serializer.validated_data['password']
        user = django_authenticate(username = username, password = password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message" : "don't match",
                "error": serializer.errors
            }, status = 400)
        
        django_login(request, user)
        return Response({
                "success": True,
                "user" : UserSerializer(instance=user).data,
        })
    
    @action(methods = ['GET'], detail = False)
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        serializer_context = {
            'request': request,
        }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user, context=serializer_context).data
        return Response(data)

    @action(methods = ['POST'], detail = False)
    def logout(self, request):
        django_logout(request)
        return Response({"success": True})

    @action(methods = ['POST'], detail = False)
    def signup(self, request):
        serializer = SignupSerializer(data =  request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message" : "don't match",
                "error": serializer.errors
            }, status = 400)
        
        user =  serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data
        })