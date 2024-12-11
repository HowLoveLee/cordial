from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re

class RegistrationForm(forms.ModelForm):
    nshe_id = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'id': 'r-nshe-id',
            'name': 'r-nshe-id',
            'placeholder': '1234567890',
            'maxlength': '10',
            'minlength': '10',
            'pattern': r'^\d{10}$',  # Ensures only numeric input
            'required': True,
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
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'id': 'r-password',
            'name': 'r-password',
            'placeholder': 'Password',
            'required': True,
        }),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'nshe_id', 'password')

    def clean_nshe_id(self):
        nshe_id = self.cleaned_data.get('nshe_id')
        if not re.match(r'^\d{10}$', nshe_id):
            raise ValidationError("NSHE ID must be exactly 10 digits.")
        return nshe_id


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'required': True,
        }),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'NSHE ID',
            'required': True,
        }),


    )
