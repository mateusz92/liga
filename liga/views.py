# -*- coding: utf-8
from django.shortcuts import render
from datetime import *
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
    leagues_list = League.objects.filter(finished=False)
    for liga in leagues_list:
        teams = League_Team.objects.filter(league=liga)
        setattr(liga, 'count', teams.count())
    finished_leagues_list = League.objects.filter(finished=True)
    for liga in finished_leagues_list:
        teams = League_Team.objects.filter(league=liga)
        setattr(liga, 'count', teams.count())
    template = loader.get_template('leagues.html')
    context = RequestContext(request, {
        'leagues_list' : leagues_list, 'finished_leagues_list' : finished_leagues_list
    })
    return HttpResponse(template.render(context))

def finishleague(request, l_id):
    leagueID = int(l_id)
    if leagueID > 0 and request.session["verified"]==True:
        league = League.objects.get(id=leagueID)
        league.finished = True
        league.save()
        teams_list = League_Team.objects.filter(league=league)
        for lt in teams_list:
            team = Team.objects.get(id=lt.team.id)
            team.available = True
            team.save()
        return redirect('/leagues')
    else:
        return redirect('/')

def league(request, l_id = "0"):
    leagueID = int(l_id)
    if leagueID < 1:
        return redirect('/')
    else:
        l = League.objects.get(id = leagueID)
        teams_list = League_Team.objects.filter(league = l)
        for tl in teams_list:
            mecze = Match.objects.filter(Q(league=l) & (Q(homeTeam=tl.team) | Q(guestTeam=tl.team)))
            punkty = 0
            stracone = 0
            strzelone = 0
            for mecz in mecze:
                if mecz.homeTeam == tl.team:
                    if mecz.homeGoals > mecz.guestGoals:
                        punkty = punkty + 3
                    if mecz.homeGoals == mecz.guestGoals:
                        punkty = punkty + 1
                    stracone = stracone + mecz.guestGoals
                    strzelone = strzelone + mecz.homeGoals
                if mecz.guestTeam == tl.team:
                    if mecz.homeGoals < mecz.guestGoals:
                        punkty = punkty + 3
                    if mecz.homeGoals == mecz.guestGoals:
                        punkty = punkty + 1
                    stracone = stracone + mecz.homeGoals
                    strzelone = strzelone + mecz.guestGoals
            tl.matchPlayed = mecze.count()
            tl.scoredGoals = strzelone
            tl.lostGoals = stracone
            tl.points = punkty
            tl.save()
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
                msg = 'Dodano zawodnika'
                f = forms.NewPlayerForm()
                return render_to_response('newPlayer.html', RequestContext(request, {'formset': f, 'msg' : msg}))
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
                msg = 'Dodano sędziego'
                f = forms.NewRefereeForm()
                return render_to_response('newReferee.html', RequestContext(request, {'formset': f, 'msg' : msg}))
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
                msg = 'Dodano trenera'
                f = forms.NewCoachForm()
                return render_to_response('newCoach.html', RequestContext(request, {'formset': f, 'msg' : msg}))
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
                msg = 'Dodano drużynę'
                f = forms.NewTeamForm()
                return render_to_response('newTeam.html', RequestContext(request, {'formset': f, 'msg' : msg}))
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
                msg = 'Dodano ligę'
                f = forms.NewLeagueForm()
                return render_to_response('newLeague.html', RequestContext(request, {'formset': f, 'msg' : msg}))
            else:
                msg = 'Niepoprawne dane'
                f = forms.NewLeagueForm()
                return render_to_response('newLeague.html', RequestContext(request, {'formset': f, 'msg' : msg}))
        else:
            f = forms.NewLeagueForm()
            return render_to_response('newLeague.html', RequestContext(request, {'formset': f}))
    else:
        return redirect('/')

def deleteleague(request, l_id):
    leagueID = int(l_id)
    if request.session["verified"]==True and leagueID>0:
        league = League.objects.get(id=leagueID)
        lts = League_Team.objects.filter(league=league)
        for lt in lts:
            lt.delete()
            team = Team.objects.get(id=lt.team.id)
            team.available = True
            team.save()
        ltps = League_Team_Player.objects.filter(league=league)
        for ltp in ltps:
            ltp.delete()
        league.delete()
        return redirect('/leagues')
    else:
        return redirect('/leagues')

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

def matches(request, t_id, l_id):
    teamID = int(t_id)
    leagueID = int(l_id)
    if teamID>0 and leagueID>0:
        mecze = Match.objects.filter((Q(homeTeam__id=teamID) | Q(guestTeam=teamID)  )& Q(league__id=leagueID))
        team = Team.objects.get(id=teamID)
        league = League.objects.get(id=leagueID)
        return render_to_response('matches.html', RequestContext(request, {'mecze': mecze, 'team':team, 'league':league}))

def newmatch(request, t_id, l_id):
    leagueID = int(l_id)
    teamID = int(t_id)
    if leagueID > 0 and teamID > 0 and request.session["verified"]==True:
        team = Team.objects.get(id=teamID)
        if request.method == 'POST':
            f = forms.NewMatch(request.POST)
            if f.is_valid():
                mecz = Match()
                mecz.date = f.cleaned_data['date']
                mecz.guestGoals = f.cleaned_data['guestGoals']
                mecz.homeGoals = f.cleaned_data['homeGoals']
                mecz.guestTeam = f.cleaned_data['guestTeam']
                mecz.homeTeam = f.cleaned_data['homeTeam']
                mecz.league = League.objects.get(id=leagueID)
                mecz.referee = f.cleaned_data['referee']
                mecz.save()
                return redirect('/matches/'+t_id+'/'+l_id+'/')
            else:
                league = League.objects.get(id=leagueID)
                f = forms.NewMatch()
                f.fields['homeTeam'].queryset = League_Team.objects.filter(league=league)
                f.fields['guestTeam'].queryset = League_Team.objects.filter(league=league)
                msg = 'Niepoprawna data'
                return render_to_response('newMatch.html', RequestContext(request, {'formset': f, 'msg' : msg, 'league':league, 'team':team}))
        else:
            league = League.objects.get(id=leagueID)
            f = forms.NewMatch()
            f.fields['homeTeam'].queryset = League_Team.objects.filter(league=league)
            f.fields['guestTeam'].queryset = League_Team.objects.filter(league=league)
            msg = ''
            return render_to_response('newMatch.html', RequestContext(request, {'formset': f, 'msg' : msg, 'league':league, 'team':team}))
    else:
        return redirect('/leagues')

def match(request, m_id):
    matchID = int(m_id)
    if matchID > 0:
        mecz = Match.objects.get(id=matchID)
        homeShoots = 0
        homeShootsOnTarget = 0
        homeOffsides = 0
        homeFouls = 0
        guestShoots = 0
        guestShootsOnTarget = 0
        guestOffsides = 0
        guestFouls = 0
        homeGoals = Goal.objects.filter(Q(match=mecz) & Q(team=mecz.homeTeam)).order_by('time')
        guestGoals = Goal.objects.filter(Q(match=mecz) & Q(team=mecz.guestTeam)).order_by('time')
        homeYellows = PlayerStats.objects.filter(Q(match=mecz) & Q(team=mecz.homeTeam) & Q(yellowCard=True))
        guestYellows = PlayerStats.objects.filter(Q(match=mecz) & Q(team=mecz.guestTeam) & Q(yellowCard=True))
        homeReds = PlayerStats.objects.filter(Q(match=mecz) & Q(team=mecz.homeTeam) & Q(redCard=True))
        guestReds = PlayerStats.objects.filter(Q(match=mecz) & Q(team=mecz.guestTeam) & Q(redCard=True))
        homeStats = PlayerStats.objects.filter(Q(match=mecz) & Q(team=mecz.homeTeam))
        for hs in homeStats:
            homeShoots += hs.shoots
            homeShootsOnTarget += hs.shootsOnTarget
            homeOffsides += hs.offsides
            homeFouls += hs.fouls
        guestStats = PlayerStats.objects.filter(Q(match=mecz) & Q(team=mecz.guestTeam))
        for gs in guestStats:
            guestShoots += gs.shoots
            guestShootsOnTarget += gs.shootsOnTarget
            guestOffsides += gs.offsides
            guestFouls += gs.fouls
        homeSubs = Substitution.objects.filter(Q(match=mecz) & Q(team=mecz.homeTeam))
        guestSubs = Substitution.objects.filter(Q(match=mecz) & Q(team=mecz.guestTeam))
        return render_to_response('match.html', RequestContext(request, {'mecz':mecz, 'homeGoals':homeGoals, 'guestGoals':guestGoals,
                                                                         'homeYellows':homeYellows, 'guestYellows':guestYellows,
                                                                         'homeReds':homeReds, 'guestReds':guestReds,
                                                                         'homeStats':homeStats, 'guestStats':guestStats,
                                                                         'homeSubs':homeSubs, 'guestSubs':guestSubs,
                                                                         'homeShoots':homeShoots, 'guestShoots':guestShoots,
                                                                         'homeShootsOnTarget':homeShootsOnTarget, 'guestShootsOnTarget':guestShootsOnTarget,
                                                                         'homeOffsides':homeOffsides, 'guestOffsides':guestOffsides,
                                                                         'homeFouls':homeFouls, 'guestFouls':guestFouls}))
    else:
        return redirect('/')

def addgoal(request, m_id, t_id):
    matchID = int(m_id)
    teamID = int(t_id)
    if matchID > 0 and teamID > 0 and request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.NewGoal(request.POST)
            if f.is_valid():
                mecz = Match.objects.get(id=matchID)
                team = Team.objects.get(id=teamID)
                goal = Goal()
                goal.player = f.cleaned_data['scorer']
                goal.match = mecz
                goal.team = team
                goal.time = f.cleaned_data['time']
                goal.isPenalty = f.cleaned_data['penalty']
                goal.save()
                return redirect('/match/'+m_id+'/')
            else:
                return redirect('/')
        else:
            mecz = Match.objects.get(id=matchID)
            team = Team.objects.get(id=teamID)
            f = forms.NewGoal()
            f.fields['scorer'].queryset = Team_Player.objects.filter(team=team)
            return render_to_response('addGoal.html', RequestContext(request, {'formset':f, 'mecz':mecz, 'team':team}))
    else:
        return redirect('/')

def deletegoal(request, g_id, m_id):
    matchID = int(m_id)
    goalID = int(g_id)
    if matchID > 0 and goalID > 0 and request.session["verified"]==True:
        goal = Goal.objects.get(id=goalID)
        goal.delete()
        return redirect('/match/'+m_id+'/')
    else:
        return redirect('/')

def addstats(request, m_id, t_id):
    matchID = int(m_id)
    teamID = int(t_id)
    if matchID > 0 and teamID > 0 and request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.NewStats(request.POST)
            if f.is_valid():
                mecz = Match.objects.get(id=matchID)
                team = Team.objects.get(id=teamID)
                stats = PlayerStats()
                stats.team = team
                stats.match = mecz
                stats.player = f.cleaned_data['player']
                stats.entryTime = f.cleaned_data['entryTime']
                stats.fouls = f.cleaned_data['fouls']
                stats.isSubstitution = f.cleaned_data['isSubstitution']
                stats.offsides = f.cleaned_data['offsides']
                stats.redCard = f.cleaned_data['red']
                stats.yellowCard = f.cleaned_data['yellow']
                stats.shoots = f.cleaned_data['shoots']
                stats.shootsOnTarget = f.cleaned_data['shootsOnTarget']
                stats.save()
                return redirect('/match/'+m_id+'/')
            else:
                return redirect('/')
        else:
            mecz = Match.objects.get(id=matchID)
            team = Team.objects.get(id=teamID)
            f = forms.NewStats()
            f.fields['player'].queryset = Team_Player.objects.filter(team=team)
            return render_to_response('addStats.html', RequestContext(request, {'formset':f, 'mecz':mecz, 'team':team}))
    else:
        return redirect('/')

def deletestats(request, s_id, m_id):
    matchID = int(m_id)
    statsID = int(s_id)
    if matchID > 0 and statsID > 0 and request.session["verified"]==True:
        stats = PlayerStats.objects.get(id=statsID)
        stats.delete()
        return redirect('/match/'+m_id+'/')
    else:
        return redirect('/')

def addsub(request, m_id, t_id):
    matchID = int(m_id)
    teamID = int(t_id)
    if matchID > 0 and teamID > 0 and request.session["verified"]==True:
        if request.method == 'POST':
            f = forms.NewSub(request.POST)
            if f.is_valid():
                mecz = Match.objects.get(id=matchID)
                team = Team.objects.get(id=teamID)
                sub = Substitution()
                sub.prevPlayer = f.cleaned_data['prevPlayer']
                sub.newPlayer = f.cleaned_data['newPlayer']
                sub.time = f.cleaned_data['time']
                sub.match = mecz
                sub.team = team
                sub.save()
                return redirect('/match/'+m_id+'/')
            else:
                return redirect('/')
        else:
            mecz = Match.objects.get(id=matchID)
            team = Team.objects.get(id=teamID)
            f = forms.NewSub()
            f.fields['prevPlayer'].queryset = Team_Player.objects.filter(team=team)
            f.fields['newPlayer'].queryset = Team_Player.objects.filter(team=team)
            return render_to_response('addSub.html', RequestContext(request, {'formset':f, 'mecz':mecz, 'team':team}))
    else:
        return redirect('/')

def deletesub(request, s_id, m_id):
    matchID = int(m_id)
    subID = int(s_id)
    if matchID > 0 and subID > 0 and request.session["verified"]==True:
        sub = Substitution.objects.get(id=subID)
        sub.delete()
        return redirect('/match/'+m_id+'/')
    else:
        return redirect('/')