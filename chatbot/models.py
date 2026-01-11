from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConversation(models.Model):
    # Null user means the interaction was anonymous
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    response = models.TextField()
    language = models.CharField(max_length=10, default='en')
    is_anonymous = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Anonymous" if self.is_anonymous else f"User: {self.user.username}"
        return f"{status} | {self.timestamp.strftime('%d-%m %H:%M')}"