from django import forms
from liga.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core import validators
class RegisterForm(forms.Form):
    login = forms.CharField(label='Login', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    password = forms.CharField(label='Hasło', max_length=50, widget=forms.PasswordInput(attrs={'size': '80'}))
    confirmpassword = forms.CharField(label='Potwierdź hasło', max_length=50, widget=forms.PasswordInput(attrs={'size': '80'}))
    email = forms.CharField(label='Email', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    name = forms.CharField(label='Nazwa użytkownika', max_length=100, widget=forms.TextInput(attrs={'size': '80'}))

class LoginForm(forms.Form):
    login = forms.CharField(label='Login', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    password = forms.CharField(label='Hasło', max_length=50, widget=forms.PasswordInput(attrs={'size': '80'}))