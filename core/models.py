from django.db import models
from .manager import CustomUserManager
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)

    USERNAME_FIELD = 'email'    # Required for log in
    REQUIRED_FIELDS = ['username'] # Required for creating a user

    objects = CustomUserManager()
    
    def __str__(self):
        return self.email


class Class(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField()
    description = models.TextField()


class Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    duration = models.IntegerField(help_text="In minutes")
    goals = models.TextField()


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=10, choices=(('user', 'User'), ('bot', 'Bot')))