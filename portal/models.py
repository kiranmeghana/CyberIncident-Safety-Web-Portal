from django.db import models
from django.conf import settings  # Import settings to reference custom user

class Incident(models.Model):
    # Use settings.AUTH_USER_MODEL instead of the 'User' class
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    incident_type = models.CharField(max_length=100) 
    description = models.TextField() 
    evidence = models.FileField(upload_to='evidence/', null=True, blank=True) 
    risk_score = models.IntegerField(default=0) 
    risk_level = models.CharField(
        max_length=20, 
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        default='Low'
    )
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='Pending') 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.incident_type} - {self.risk_level} ({self.status})"