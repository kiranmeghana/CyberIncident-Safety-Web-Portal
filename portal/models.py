from django.db import migrations, models
from django.contrib.auth.models import User

class Incident(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    incident_type = models.CharField(max_length=100) 
    description = models.TextField() 
    evidence = models.FileField(upload_to='evidence/') 
    risk_score = models.IntegerField(default=0) 
    risk_level = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='Pending') 
    created_at = models.DateTimeField(auto_now_add=True)

class ChatLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    response = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)