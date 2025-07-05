from django.contrib import admin
from .models import User, Class, Plan, ChatMessage

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username')
    search_fields = ('email', 'username')
    list_filter = ('is_active',)
    ordering = ('-id',)

