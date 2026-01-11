from django.contrib import admin
from .models import ChatConversation

@admin.register(ChatConversation)
class ChatBotAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_anonymous', 'language', 'timestamp', 'message_snippet')
    list_filter = ('is_anonymous', 'language', 'timestamp')
    search_fields = ('message', 'response')

    def message_snippet(self, obj):
        return obj.message[:50] + "..."