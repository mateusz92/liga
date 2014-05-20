from django.shortcuts import render
from datetime import datetime
from django.db.utils import ConnectionDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import loader, RequestContext
from django.http import HttpResponseRedirect
from liga import forms
from liga.models import *
from django.db.models import Q, Count


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

def currentteamsquad(request, t_id = "0"):
    teamID = int(t_id)
    if teamID < 1:
        return redirect('/')
    else:
        t = Team.objects.get(id = teamID)
        coach = t.coach
        players_list = Team_Player.objects.filter(team = t)
        template = loader.get_template('currentTeamSquad.html')
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
    del request.session["verified"]
    request.session.modified = True
    return redirect('/')

def newplayer(request):
    if request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.NewPlayerForm(request.POST)
            if f.is_valid():
                czy_jest = Player.objects.filter(Q(name=f.cleaned_data['name']) & Q(surname=f.cleaned_data['surname'])).count()
                if czy_jest > 0:
                    msg = 'Zawodnik już istnieje'
                    f = forms.NewPlayerForm()
                    return render_to_response('newPlayer.html', RequestContext(request, {'formset': f, 'msg' : msg}))
                player = Player()
                player.name = f.cleaned_data['name']
                player.surname = f.cleaned_data['surname']
                player.available = True
                player.save()
                f = forms.NewPlayerForm()
                return render_to_response('newPlayer.html', RequestContext(request, {'formset': f}))
            else:
                msg = 'Niepoprawne dane'
                f = forms.NewPlayerForm()
                return render_to_response('newPlayer.html', RequestContext(request, {'formset': f, 'msg' : msg}))
        else:
            f = forms.NewPlayerForm()
            return render_to_response('newPlayer.html', RequestContext(request, {'formset': f}))
    else:
        return redirect('/')

def players(request):
    palyerslist = Player.objects.all().order_by('surname')
    return render_to_response('players.html', RequestContext(request, {'palyerslist': palyerslist}))

def deleteplayer(request, p_id = "0"):
    playerID = int(p_id)
    if playerID > 0 and request.session["verified"]==True:
        player = Player.objects.get(id=playerID)
        player.delete()
        palyerslist = Player.objects.all().order_by('surname')
        return render_to_response('players.html', RequestContext(request, {'palyerslist': palyerslist}))
    else:
        return redirect('/')

def newreferee(request):
    if request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.NewRefereeForm(request.POST)
            if f.is_valid():
                czy_jest = Referee.objects.filter(Q(name=f.cleaned_data['name']) & Q(surname=f.cleaned_data['surname'])).count()
                if czy_jest > 0:
                    msg = 'Sędzia już istnieje'
                    f = forms.NewRefereeForm()
                    return render_to_response('newReferee.html', RequestContext(request, {'formset': f, 'msg' : msg}))
                referee = Referee()
                referee.name = f.cleaned_data['name']
                referee.surname = f.cleaned_data['surname']
                referee.save()
                f = forms.NewRefereeForm()
                return render_to_response('newReferee.html', RequestContext(request, {'formset': f}))
            else:
                msg = 'Niepoprawne dane'
                f = forms.NewRefereeForm()
                return render_to_response('newReferee.html', RequestContext(request, {'formset': f, 'msg' : msg}))
        else:
            f = forms.NewRefereeForm()
            return render_to_response('newReferee.html', RequestContext(request, {'formset': f}))
    else:
        return redirect('/')

def referees(request):
    refereeslist = Referee.objects.all().order_by('surname')
    return render_to_response('referees.html', RequestContext(request, {'refereeslist': refereeslist}))

def deletereferee(request, r_id = "0"):
    refereeID = int(r_id)
    if refereeID > 0 and request.session["verified"]==True:
        player = Referee.objects.get(id=refereeID)
        player.delete()
        refereeslist = Referee.objects.all().order_by('surname')
        return render_to_response('referees.html', RequestContext(request, {'refereeslist': refereeslist}))
    else:
        return redirect('/')

def newcoach(request):
    if request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.NewCoachForm(request.POST)
            if f.is_valid():
                czy_jest = Coach.objects.filter(Q(name=f.cleaned_data['name']) & Q(surname=f.cleaned_data['surname'])).count()
                if czy_jest > 0:
                    msg = 'Trener już istnieje'
                    f = forms.NewCoachForm()
                    return render_to_response('newCoach.html', RequestContext(request, {'formset': f, 'msg' : msg}))
                coach = Coach()
                coach.name = f.cleaned_data['name']
                coach.surname = f.cleaned_data['surname']
                coach.save()
                f = forms.NewCoachForm()
                return render_to_response('newCoach.html', RequestContext(request, {'formset': f}))
            else:
                msg = 'Niepoprawne dane'
                f = forms.NewCoachForm()
                return render_to_response('newCoach.html', RequestContext(request, {'formset': f, 'msg' : msg}))
        else:
            f = forms.NewCoachForm()
            return render_to_response('newCoach.html', RequestContext(request, {'formset': f}))
    else:
        return redirect('/')

def coaches(request):
    coacheslist = Coach.objects.all().order_by('surname')
    return render_to_response('coaches.html', RequestContext(request, {'coacheslist': coacheslist}))

def deletecoach(request, c_id = "0"):
    coachID = int(c_id)
    if coachID > 0 and request.session["verified"]==True:
        coach = Coach.objects.get(id=coachID)
        coach.delete()
        coacheslist = Coach.objects.all().order_by('surname')
        return render_to_response('coaches.html', RequestContext(request, {'coacheslist': coacheslist}))
    else:
        return redirect('/')

def newteam(request):
    if request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.NewTeamForm(request.POST)
            if f.is_valid():
                czy_jest = Team.objects.filter(name=f.cleaned_data['name']).count()
                if czy_jest > 0:
                    msg = 'Drużyna już istnieje'
                    f = forms.NewTeamForm()
                    return render_to_response('newTeam.html', RequestContext(request, {'formset': f, 'msg' : msg}))
                team = Team()
                team.name = f.cleaned_data['name']
                team.coach = f.cleaned_data['coach']
                team.available = True
                team.save()
                f = forms.NewTeamForm()
                return render_to_response('newTeam.html', RequestContext(request, {'formset': f}))
            else:
                msg = 'Niepoprawne dane'
                f = forms.NewTeamForm()
                return render_to_response('newTeam.html', RequestContext(request, {'formset': f, 'msg' : msg}))
        else:
            f = forms.NewTeamForm()
            return render_to_response('newTeam.html', RequestContext(request, {'formset': f}))
    else:
        return redirect('/')

def teams(request):
    teamslist = Team.objects.all().order_by('name')
    return render_to_response('teams.html', RequestContext(request, {'teamslist': teamslist}))

def deleteteam(request, t_id = "0"):
    teamID = int(t_id)
    if teamID > 0 and request.session["verified"]==True:
        team = Team.objects.get(id=teamID)
        team.delete()
        teamslist = Team.objects.all().order_by('name')
        return render_to_response('teams.html', RequestContext(request, {'teamslist': teamslist}))
    else:
        return redirect('/')

def editteam(request, t_id = "0"):
    if request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.AddPlayerToTeamForm(request.POST)
            if f.is_valid():
                player = f.cleaned_data['player']
                player.available = False
                teamID = int(t_id)
                t = Team.objects.get(id = teamID)
                tp = Team_Player()
                tp.team = t;
                tp.player = player
                player.save()
                tp.save()
                coach = t.coach
                players_list = Team_Player.objects.filter(team = t)
                f = forms.AddPlayerToTeamForm()
                cf = forms.EditTeamCoachForm({'coach': coach.pk})
                return render_to_response('editTeam.html', RequestContext(request, {'players_list': players_list, 'team': t, 'coach':coach, 'playerform': f, 'coachform': cf}))
            else:
                teamID = int(t_id)
                t = Team.objects.get(id = teamID)
                coach = t.coach
                players_list = Team_Player.objects.filter(team = t)
                f = forms.AddPlayerToTeamForm()
                cf = forms.EditTeamCoachForm({'coach': coach.pk})
                return render_to_response('editTeam.html', RequestContext(request, {'players_list': players_list, 'team': t, 'coach':coach, 'playerform': f, 'coachform': cf}))
        else:
            teamID = int(t_id)
            if teamID < 1:
                return redirect('/')
            else:
                t = Team.objects.get(id = teamID)
                coach = t.coach
                players_list = Team_Player.objects.filter(team = t)
                f = forms.AddPlayerToTeamForm()
                cf = forms.EditTeamCoachForm({'coach': coach.pk})
                return render_to_response('editTeam.html', RequestContext(request, {'players_list': players_list, 'team': t, 'coach':coach, 'playerform': f, 'coachform': cf}))
    else:
        return redirect('/')

def deleteplayerfromteam(request, p_id="0", t_id="0"):
    teamID = int(t_id)
    playerID = int(p_id)
    if teamID > 0 and playerID > 0 and request.session["verified"]==True:
        team = Team.objects.get(id=teamID)
        player = Player.objects.get(id=playerID)
        tp = Team_Player.objects.get(team=team, player=player)
        tp.delete()
        player.available = True
        player.save()
        coach = team.coach
        players_list = Team_Player.objects.filter(team = team)
        f = forms.AddPlayerToTeamForm()
        cf = forms.EditTeamCoachForm({'coach': coach.pk})
        return render_to_response('editTeam.html', RequestContext(request, {'players_list': players_list, 'team': team, 'coach':coach, 'playerform': f, 'coachform': cf}))
    else:
        return redirect('/')

def editteamcoach(request, t_id = "0"):
    teamID = int(t_id)
    if request.session["verified"]==True and teamID > 0:
        if request.method == 'POST':
            f = forms.EditTeamCoachForm(request.POST)
            if f.is_valid():
                t = Team.objects.get(id = teamID)
                t.coach = f.cleaned_data['coach']
                t.save()
                coach = t.coach
                players_list = Team_Player.objects.filter(team = t)
                f = forms.AddPlayerToTeamForm()
                cf = forms.EditTeamCoachForm({'coach': coach.pk})
                return render_to_response('editTeam.html', RequestContext(request, {'players_list': players_list, 'team': t, 'coach':coach, 'playerform': f, 'coachform': cf}))
            else:
                teamID = int(t_id)
                t = Team.objects.get(id = teamID)
                coach = t.coach
                players_list = Team_Player.objects.filter(team = t)
                f = forms.AddPlayerToTeamForm()
                cf = forms.EditTeamCoachForm({'coach': coach.pk})
                return render_to_response('editTeam.html', RequestContext(request, {'players_list': players_list, 'team': t, 'coach':coach, 'playerform': f, 'coachform': cf}))
        else:
            teamID = int(t_id)
            if teamID < 1:
                return redirect('/')
            else:
                t = Team.objects.get(id = teamID)
                coach = t.coach
                players_list = Team_Player.objects.filter(team = t)
                f = forms.AddPlayerToTeamForm()
                cf = forms.EditTeamCoachForm({'coach': coach.pk})
                return render_to_response('editTeam.html', RequestContext(request, {'players_list': players_list, 'team': t, 'coach':coach, 'playerform': f, 'coachform': cf}))
    else:
        return redirect('/')

def newleague(request):
    if request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.NewLeagueForm(request.POST)
            if f.is_valid():
                czy_jest = League.objects.filter(name=f.cleaned_data['name']).count()
                if czy_jest > 0:
                    msg = 'Liga już istnieje'
                    f = forms.NewLeagueForm()
                    return render_to_response('newLeague.html', RequestContext(request, {'formset': f, 'msg' : msg}))
                league = League()
                league.name = f.cleaned_data['name']
                league.finished = False
                league.save()
                f = forms.NewLeagueForm()
                return render_to_response('newLeague.html', RequestContext(request, {'formset': f}))
            else:
                msg = 'Niepoprawne dane'
                f = forms.NewLeagueForm()
                return render_to_response('newLeague.html', RequestContext(request, {'formset': f, 'msg' : msg}))
        else:
            f = forms.NewLeagueForm()
            return render_to_response('newLeague.html', RequestContext(request, {'formset': f}))
    else:
        return redirect('/')

def editleagueteams(request, l_id = "0"):
    if request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.AddTeamToLeagueForm(request.POST)
            if f.is_valid():
                team = f.cleaned_data['team']
                team.available = False
                team.save()
                leagueID = int(l_id)
                l = League.objects.get(id = leagueID)
                lt = League_Team()
                lt.team = team
                lt.points = 0
                lt.scoredGoals = 0
                lt.lostGoals = 0
                lt.matchPlayed = 0
                lt.league = l
                lt.save()
                tps = Team_Player.objects.filter(team=team)
                for tp in tps:
                    ltp = League_Team_Player()
                    ltp.league = l
                    ltp.team = team
                    ltp.player = tp.player
                    ltp.save()
                teams_list = League_Team.objects.filter(league=l)
                f = forms.AddTeamToLeagueForm()
                return render_to_response('editLeagueTeams.html', RequestContext(request, {'teams_list': teams_list, 'league': l, 'teamform': f}))
            else:
                leagueID = int(l_id)
                l = League.objects.get(id = leagueID)
                teams_list = League_Team.objects.filter(league=l)
                f = forms.AddTeamToLeagueForm()
                return render_to_response('editLeagueTeams.html', RequestContext(request, {'teams_list': teams_list, 'league': l, 'teamform': f}))
        else:
            leagueID = int(l_id)
            if leagueID < 1:
                return redirect('/')
            else:
                leagueID = int(l_id)
                l = League.objects.get(id = leagueID)
                teams_list = League_Team.objects.filter(league=l)
                f = forms.AddTeamToLeagueForm()
                return render_to_response('editLeagueTeams.html', RequestContext(request, {'teams_list': teams_list, 'league': l, 'teamform': f}))
    else:
        return redirect('/')

def deleteteamfromleague(request, t_id="0", l_id="0"):
    teamID = int(t_id)
    leagueID = int(l_id)
    if teamID > 0 and leagueID > 0 and request.session["verified"]==True:
        team = Team.objects.get(id=teamID)
        league = League.objects.get(id=leagueID)
        lt = League_Team.objects.get(Q(team=team) & Q(league=league))
        lt.delete()
        team.available = True
        team.save()
        ltps = League_Team_Player.objects.filter(Q(team=team) & Q(league=league))
        for ltp in ltps:
            ltp.delete()
        teams_list = League_Team.objects.filter(league=league)
        f = forms.AddTeamToLeagueForm()
        return render_to_response('editLeagueTeams.html', RequestContext(request, {'teams_list': teams_list, 'league': league, 'teamform': f}))
    else:
        return redirect('/')