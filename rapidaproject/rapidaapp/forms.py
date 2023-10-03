from django import forms
#from rapidaapp.models import User
from django.contrib.auth.models import User 


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username', 'class': 'form-field'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-field'}),
        }

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
        ]
        widgets = {
            'validate': forms.TextInput(),
        }