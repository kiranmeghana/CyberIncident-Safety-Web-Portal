from django import forms
from .models import Incident

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['incident_type', 'description', 'evidence', 'is_anonymous']
        widgets = {
            'incident_type': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-3 border rounded-lg', 'rows': 4, 'placeholder': 'Describe the incident...'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600'}),
        }