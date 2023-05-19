from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    role = forms.CharField(max_length=20, required=False)
    id_number = forms.CharField(max_length=20, required=False)
    
    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        return ' '.join([word.capitalize() for word in full_name.split()])

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'role', 'id_number']
