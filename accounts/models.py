from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'General User/Defence Personnel'),
        ('admin', 'Admin/Analyst'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    anonymous_id = models.UUIDField(default=uuid.uuid4, editable=False)
    is_approved = models.BooleanField(default=True) # Default True for general users
    login_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.username} ({self.role})"

class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"