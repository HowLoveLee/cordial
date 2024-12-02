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
    nshe_id = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'id': 'r-nshe-id',
            'name': 'r-nshe-id',
            'placeholder': 'NSHE-ID',
            'required': True,
        })
    )
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'id': 'r-username',
            'name': 'r-username',
            'placeholder': 'Username: Non-editable',
            'readonly': True,
            'required': True,
        }),
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
        fields = ('first_name', 'last_name', 'email', 'nshe_id', 'username', 'password')


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
