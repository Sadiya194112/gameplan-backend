from django.urls import path
from . import views

urlpatterns = [
    # -------------Authentication URLs-------------
    path('register/', views.register, name='register'),
    path('verification-code/', views.verifyOTP, name='verify-otp'),
    path('reset-password/', views.ResetPassword, name='forget-password'),
    path('password-reset-confirm/', views.PasswordResetConfirm, name='password-reset-confirm'),
    
    path("create-payment/", views.CreatePaymentAPI, name='create-payment'),
    path("success/", views.success, name='success'),
    path("cancel/", views.cancel, name="cancel"),
    
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    path('class/', views.class_list_create, name='class-list-create'),
    path('plan/', views.plan_list_create, name='plan-list-create'),
    path('chats/', views.chat_list_create, name='chat-list-create'),
    
    path('ai-chat/', views.chat_with_ai, name='chat-with-ai')
]

