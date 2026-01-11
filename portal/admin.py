from django.contrib import admin
from .models import Incident

class IncidentAdmin(admin.ModelAdmin):
    # Features: Filtering and Tagging (Anonymous vs User)
    list_display = ('incident_type', 'is_anonymous', 'risk_level', 'status', 'created_at')
    list_filter = ('risk_level', 'status', 'is_anonymous')
    search_fields = ('incident_type', 'description')
    
    # Custom colored status display
    def get_risk_highlight(self, obj):
        if obj.risk_score >= 8:
            return "RED GLOW FLAG" # This will be handled in the custom dashboard template