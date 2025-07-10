from django.contrib import admin
from .models import User, Class, Plan, ChatMessage

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username')
    search_fields = ('email', 'username')
    list_filter = ('is_active',)
    ordering = ('-id',)



@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question_short', 'topic', 'timestamp')
    search_fields = ('user__username', 'question', 'answer', 'topic')
    list_filter = ('topic', 'timestamp')
    ordering = ('-timestamp',)
    

    def question_short(self, obj):
        return (obj.question[:75] + '...') if len(obj.question) > 75 else obj.question
    question_short.short_description = 'Question'
    

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'title', 'description', 'date']


@admin.register(Class)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'title', 'duration', 'goals']