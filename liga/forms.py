# -*- coding: utf-8
from django import forms
from datetime import *
from liga.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core import validators
from django.contrib.admin.widgets import AdminDateWidget

class RegisterForm(forms.Form):
    login = forms.CharField(label='Login', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    password = forms.CharField(label='Hasło', max_length=50, widget=forms.PasswordInput(attrs={'size': '80'}))
    confirmpassword = forms.CharField(label='Potwierdź hasło', max_length=50, widget=forms.PasswordInput(attrs={'size': '80'}))
    email = forms.CharField(label='Email', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    name = forms.CharField(label='Nazwa wyświetlana', max_length=100, widget=forms.TextInput(attrs={'size': '80'}))

class LoginForm(forms.Form):
    login = forms.CharField(label='Login', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    password = forms.CharField(label='Hasło', max_length=50, widget=forms.PasswordInput(attrs={'size': '80'}))

class NewPlayerForm(forms.Form):
    name = forms.CharField(label='Imię', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    surname = forms.CharField(label='Nazwisko', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))

class NewRefereeForm(forms.Form):
    name = forms.CharField(label='Imię', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    surname = forms.CharField(label='Nazwisko', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))

class NewCoachForm(forms.Form):
    name = forms.CharField(label='Imię', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    surname = forms.CharField(label='Nazwisko', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))

class NewTeamForm(forms.Form):
    name = forms.CharField(label='Nazwa', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))
    coach = forms.ModelChoiceField(queryset=Coach.objects.all(),label='Trener',initial=0)

class NewLeagueForm(forms.Form):
    name = forms.CharField(label='Nazwa', max_length=50, widget=forms.TextInput(attrs={'size': '80'}))

class AddPlayerToTeamForm(forms.Form):
    player = forms.ModelChoiceField(queryset=Player.objects.filter(available=True),label='Zawodnik', initial=0)

class AddTeamToLeagueForm(forms.Form):
    team = forms.ModelChoiceField(queryset=Team.objects.filter(available=True),label='Drużyna', initial=0)

class EditTeamCoachForm(forms.Form):
    coach = forms.ModelChoiceField(queryset=Coach.objects.all(),label='Trener')

class NewMatch(forms.Form):
    homeTeam = forms.ModelChoiceField(queryset=Team.objects.all(),label='Gospodarz', initial=0, widget=forms.Select(attrs={'style': 'width:200px'}))
    guestTeam = forms.ModelChoiceField(queryset=Team.objects.all(),label='Gość', initial=0, widget=forms.Select(attrs={'style': 'width:200px'}))
    homeGoals = forms.IntegerField(label='Gole gospodarza', initial=0, widget=forms.NumberInput(attrs={'style': 'width:50px', 'min': '0', 'max': '10', 'step': '1'}))
    guestGoals = forms.IntegerField(label='Gole gościa', initial=0, widget=forms.NumberInput(attrs={'style': 'width:50px', 'min': '0', 'max': '10', 'step': '1'}))
    date = forms.DateField(label='Data', initial=date.today)
    referee = forms.ModelChoiceField(queryset=Referee.objects.all(), label='Sędzia', initial=0)