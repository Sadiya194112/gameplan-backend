from django.urls import path
from . import views

urlpatterns = [
    # -------------Authentication URLs-------------
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    path('class/', views.class_list_create, name='class-list-create'),
    path('plan/', views.plan_list_create, name='plan-list-create'),
    path('chat/', views.chat_list_create, name='chat-list-create'),
]
