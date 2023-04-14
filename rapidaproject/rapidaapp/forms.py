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
            'validate': forms.TextInput(),
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