from django.shortcuts import render
from datetime import datetime
from django.db.utils import ConnectionDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import loader, RequestContext
from django.http import HttpResponseRedirect
from liga import forms
from liga.models import *


def home(request):
    template = loader.get_template('home.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def leagues(request):
    leagues_list = League.objects.all()
    for liga in leagues_list:
        teams = League_Team.objects.filter(league=liga)
        setattr(liga, 'count', teams.count())
    template = loader.get_template('leagues.html')
    context = RequestContext(request, {
        'leagues_list' : leagues_list
    })
    return HttpResponse(template.render(context))

def league(request, l_id = "0"):
    leagueID = int(l_id)
    if leagueID < 1:
        return redirect('/')
    else:
        l = League.objects.get(id = leagueID)
        teams_list = League_Team.objects.filter(league = l)
        template = loader.get_template('league.html')
        context = RequestContext(request, {
            'teams_list' : teams_list,
            'league' : l
        })
        return HttpResponse(template.render(context))

def team(request, t_id = "0", l_id = "0"):
    teamID = int(t_id)
    leagueID = int(l_id)
    if teamID < 1:
        return redirect('/')
    else:
        t = Team.objects.get(id = teamID)
        l = League.objects.get(id = leagueID)
        coach = t.coach
        players_list = League_Team_Player.objects.filter(league = l, team = t)
        template = loader.get_template('team.html')
        context = RequestContext(request, {
            'players_list' : players_list,
            'team' : t,
            'coach' : coach
        })
        return HttpResponse(template.render(context))
def register(request):
    if request.method == 'POST':
        f = forms.RegisterForm(request.POST)
        if f.is_valid() and f.cleaned_data['password']==f.cleaned_data['confirmpassword']:
            user = User()
            user.login = f.cleaned_data['login']
            user.password = f.cleaned_data['password']
            user.email = f.cleaned_data['email']
            user.name = f.cleaned_data['name']
            user.verified = False
            user.save()
            return redirect('/')
        else:
            msg = 'Niepoprawne dane rejestracji'
            f = forms.RegisterForm()
            return render_to_response('register.html', RequestContext(request, {'formset': f, 'msg' : msg}))
    else:
        f = forms.RegisterForm()
        return render_to_response('register.html', RequestContext(request, {'formset': f}))

def login(request):
    if request.method == 'POST':
        f = forms.LoginForm(request.POST)
        if f.is_valid():
            user = User.objects.get(login=f.cleaned_data['login'])
            if user!='' and user.password==f.cleaned_data['password']:
                request.session["user"]=user.login
                request.session["verified"] = user.verified
                return redirect('/')
            else:
                msg = 'Niepoprawne dane logowania'
                f = forms.LoginForm()
                return render_to_response('login.html', RequestContext(request, {'formset': f, 'msg' : msg}))
        else:
            msg = 'Niepoprawne dane logowania'
            f = forms.LoginForm()
            return render_to_response('login.html', RequestContext(request, {'formset': f, 'msg' : msg}))
    else:
        f = forms.LoginForm()
        return render_to_response('login.html', RequestContext(request, {'formset': f}))

def logout(request):
    del request.session["user"]
    request.session.modified = True
    return redirect('/')