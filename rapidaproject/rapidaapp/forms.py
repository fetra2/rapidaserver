from django import forms
#from rapidaapp.models import User
from django.contrib.auth.models import User 


class UserForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password1',
            'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username', 'class': 'form-field'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-field'}),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return password2

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
        ]
        widgets = {
            'password': forms.PasswordInput(),  # Use PasswordInput widget for the password field
            'validate': forms.TextInput(),
        }