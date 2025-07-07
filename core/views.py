from .serializers import *
from .emails import send_otp
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Class, Plan, ChatMessage
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

# from core.ai.Local_lama import ChatbotService    # Import your AI service here


User = get_user_model()
token_generator = PasswordResetTokenGenerator()

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
            email = serializer.validated_data.get('email')
            if User.objects.filter(email=email).exists():
                return Response({"error": "This email is already registered!"}, status=status.HTTP_400_BAD_REQUEST)
        
            user = serializer.save()
            send_otp(serializer.validated_data['email'])
            return Response({"message": "Signup Successful! Please verify your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


@api_view(['POST'])
def verifyOTP(request):
    if request.method == 'POST':
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            otp = serializer.validated_data.get('otp')
        
            user = get_object_or_404(User, email=email)
        
            if user.otp != otp:
                return Response({'msg':"Wrong Otp"}, status=status.HTTP_400_BAD_REQUEST)
     
            user.is_verified = True
            user.save()
            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
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


from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

@api_view(['POST'])
def ResetPassword(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        user = get_object_or_404(User, email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        
        reset_url = f"http://localhost:3000/api/reset-password/{uidb64}/{token}/"
        
        send_mail(
            subject="Password Reset",
            message=f"Click the link to reset your password: {reset_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def PasswordResetConfirm(request):
    serializer = SetNewPasswordSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


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
    

# Create a payment 
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def CreatePaymentAPI(request):
    if request.method == 'POST':
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                 {'price': settings.STRIPE_RECURRING_PRICE_ID, 'quantity': 1}
            ],
            mode='subscription',
            success_url='http://localhost:8000/api/success',
            cancel_url='http://localhost:8000/api/cancel',
        )
        return Response({'checkout_url': checkout_session.url})
    

def success(request):
    return Response({'message': 'Payment successful!'}, status=status.HTTP_200_OK)

def cancel(request):
    return Response({'message': 'Payment cancelled!'}, status=status.HTTP_400_BAD_REQUEST)


# -----------# AI Chatbot View------------
# chatbot = ChatbotService()  # Initialize your AI service

# @api_view(['POST'])
# def chat_with_ai(request):
#     serializer = ChatMessageSerializer(data=request.data)
#     if serializer.is_valid():
#         user_question = serializer.validated_data.get('question')
#         if not user_question:
#             return Response({'error': 'Question is required'}, status=status.HTTP_400_BAD_REQUEST)
        
#         chat_history = chatbot.load_chat_history()
        
#         # Use your AI service to get a response
#         ai_response = chatbot.get_response(user_question, chat_history)
        
#         # Save the chat message
#         chat_history.append({'role': 'user', 'content': user_question})
#         chat_history.append({'role': 'assistant', 'content': ai_response['answer']})
#         chatbot.save_chat_history(chat_history)
    
#         return Response({
#             'question': user_question,
#             'answer': ai_response['answer'],
#             'sources': [doc.page_content for doc in ai_response['source_documents']]
#         }, status=status.HTTP_200_OK)   
                
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
