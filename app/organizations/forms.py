from django import forms
from .models import Organization, Invitation

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description']

class InviteForm(forms.Form):
    email = forms.EmailField(label='Email пользователя')
