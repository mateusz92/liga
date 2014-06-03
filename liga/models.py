# -*- coding: utf-8
from django.db import models

class Coach(models.Model):
    name=models.CharField(max_length=50)
    surname=models.CharField(max_length=50)
    def __str__(self):  # Python 3: def __str__(self):
        return self.name + " " + self.surname

class User(models.Model):
    login = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    type = models.IntegerField(default=1)
    name=models.CharField(max_length=100)
    verified= models.BooleanField()
    def __str__(self):  # Python 3: def __str__(self):
        return self.name

class Team(models.Model):
    name=models.CharField(max_length=50)
    available= models.BooleanField()
    coach=models.ForeignKey(Coach)
    def __str__(self):  # Python 3: def __str__(self):
        return self.name

class League(models.Model):
    name=models.CharField(max_length=50)
    finished= models.BooleanField()
    def __str__(self):  # Python 3: def __str__(self):
        return self.name

class Player(models.Model):
    name=models.CharField(max_length=50)
    surname=models.CharField(max_length=50)
    available=models.BooleanField()
    def __str__(self):  # Python 3: def __str__(self):
        return self.name + " " + self.surname

class Referee(models.Model):
    name=models.CharField(max_length=50)
    surname=models.CharField(max_length=50)
    def __str__(self):  # Python 3: def __str__(self):
        return self.name + " " + self.surname

class Match(models.Model):
    homeTeam=models.ForeignKey(Team, related_name='homeTeam')
    guestTeam=models.ForeignKey(Team, related_name='guestTeam')
    homeGoals=models.IntegerField()
    guestGoals=models.IntegerField()
    date=models.DateField()
    league=models.ForeignKey(League)
    referee=models.ForeignKey(Referee)
    def __str__(self):  # Python 3: def __str__(self):
        return self.homeTeam.name + "-" + self.guestTeam.name

class Goal(models.Model):
    player=models.ForeignKey(Player)
    time=models.IntegerField()
    match=models.ForeignKey(Match)
    isPenalty=models.BooleanField()
    def __str__(self):  # Python 3: def __str__(self):
        return self.player.surname +  ":" + str(self.time)

class Substitution(models.Model):
    newPlayer=models.ForeignKey(Player,related_name='new_Player')
    prevPlayer=models.ForeignKey(Player,related_name='prev_Player')
    time=models.IntegerField()
    match=models.ForeignKey(Match)
    team=models.ForeignKey(Team)
    def __str__(self):  # Python 3: def __str__(self):
        return self.prevPlayer.surname + "->" + self.newPlayer.surname

class League_Team(models.Model):
    points=models.IntegerField()
    scoredGoals=models.IntegerField()
    lostGoals=models.IntegerField()
    matchPlayed=models.IntegerField()
    team=models.ForeignKey(Team)
    league=models.ForeignKey(League)
    def __str__(self):  # Python 3: def __str__(self):
        return self.league.name + "-" + self.team.name

class PlayerStats(models.Model):
    match=models.ForeignKey(Match)
    team=models.ForeignKey(Team)
    player=models.ForeignKey(Player)
    isSubstitution=models.BooleanField()
    entryTime=models.IntegerField()
    shoots=models.IntegerField()
    shootsOnTarget=models.IntegerField()
    fouls=models.IntegerField()
    offsides=models.IntegerField()
    yellowCard=models.BooleanField()
    redCart=models.BooleanField()
    def __str__(self):  # Python 3: def __str__(self):
        return self.player.surname + " stats"

class League_Team_Player(models.Model):
    league=models.ForeignKey(League)
    team=models.ForeignKey(Team)
    player=models.ForeignKey(Player)
    def __str__(self):  # Python 3: def __str__(self):
        return self.league.name + "-" + self.team.name + "-" + self.player.surname

class Team_Player(models.Model):
    team=models.ForeignKey(Team)
    player=models.ForeignKey(Player)
    def __str__(self):  # Python 3: def __str__(self):
        return self.team.name + "-" + self.player.surname