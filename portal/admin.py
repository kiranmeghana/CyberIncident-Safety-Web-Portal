from django.contrib import admin
from .models import Incident, ChatLog

@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_anonymous', 'timestamp', 'message_snippet')
    list_filter = ('is_anonymous', 'timestamp')

    def message_snippet(self, obj):
        return obj.message[:50]