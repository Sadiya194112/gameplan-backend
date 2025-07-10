from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .models import User, Class, Plan, ChatMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator


User = get_user_model()
token_generator = PasswordResetTokenGenerator()

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Password and Confirm Password do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Invalid reset link')

        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError('Invalid or expired token.')
        
        user.set_password(data['password'])
        user.save()       
        return {"message": "Password reset successful"} 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'bio', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class ClassSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()   
    
    def create(self, validated_data):
        return Class.objects.create(**validated_data)


class GETClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'user', 'title', 'description']
    

class PlanSerializer(serializers.Serializer):
    title = serializers.CharField()
    duration = serializers.CharField()
    goals = serializers.CharField()



class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_id', 'question', 'topic']


class GETChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_id', 'user', 'question', 'answer', 'topic', 'timestamp']
