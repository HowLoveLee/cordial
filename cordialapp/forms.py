from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'type': 'text',
            'id': 'r-email',
            'name': 'r-email',
            'placeholder': '1234567890@student.csn.edu',
            'required': True,
            'pattern': r'^[\w.-]+@student\.csn\.edu$',  # Ensures the email ends with @student.csn.edu
        })
    )
    first_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'id': 'r-first-name',
            'name': 'r-first-name',
            'placeholder': 'First Name',
            'required': True,
        })
    )
    last_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'id': 'r-last-name',
            'name': 'r-last-name',
            'placeholder': 'Last Name',
            'required': True,
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={
            'placeholder': 'Email',
            'required': True,
        }),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'NSHE ID',
            'required': True,
        }),
        min_length=10,
        max_length=10,
    )
