from django.shortcuts import render
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Class, Plan, ChatMessage
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .serializers import RegisterSerializer, LoginSerializer, ClassSerializer, PlanSerializer, ChatMessageSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

#  Register a new user
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


# Login & return JWT
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')    
            password = serializer.data.get('password')
            user = authenticate(request, email=email, password=password)  # Authenticate using email as username
            # breakpoint()
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({'token': token,'message': 'Login Success'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    if request.method == 'POST':
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)

# ----------CLASS VIEWS ----------

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def class_list_create(request):
    if request.method == 'GET':
        classes = Class.objects.filter(user=request.user)
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# -----------PLAN VIEWS-----------

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def plan_list_create(request):
    if request.method == 'GET':
        plans = Plan.objects.filter(user=request.user)
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      


# -----------CHAT MESSAGE VIEWS-----------
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def chat_list_create(request):
    if request.method == 'GET':
        messages = ChatMessage.objects.filter(user=request.user)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)