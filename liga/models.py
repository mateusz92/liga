from django.db import models

# Create your models here.
##fdfsdfsdfsgfdg
class User(models.Model):
    login = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    type = models.IntegerField(default=1)
    name=models.CharField(max_length=100)
    verified= models.BooleanField()

class Team(models.Model):
    name=models.CharField(max_length=50)
    available= models.BooleanField()
    coachID=models.ForeignKey(Coach)

class Player(models.Model):
    name=models.CharField()
    surname=models.CharField()
    available=models.BooleanField()
class Referee(models.Model):
    name=models.CharField(max_length=50)
    surname=models.CharField(max_length=50)
class Match(models.Model):
    homeTeam=models.ForeignKey(Team)
    guestTeam=models.ForeignKey(Team)
    homeGoals=models.IntegerField()
    guestGoals=models.IntegerField()
    date=models.DateField()
    leagueID=models.ForeignKey(League)
    refereeID=models.ForeignKey(Referee)

class Goal(models.Model):
    playetID=models.ForeignKey(Player)
    time=models.IntegerField
    matchID=models.ForeignKey(Match)
    isPenalty=models.BooleanField()
class Substitution(models.Model):
    newPlayerID=models.ForeignKey(Player)
    prevPlayerID=models.ForeignKey(Player)
    time=models.IntegerField()
    matchID=models.ForeignKey(Match)
    teamID=models.ForeignKey(Team)
class Coach(models.Model):
    name=models.CharField()
    surname=models.CharField()
class League(models.Model):
    name=models.CharField()
    teamID=models.ManyToManyField(League_Team)

class League_Team(models.Model):
    points=models.IntegerField()
    scoredGoals=models.IntegerField()
    lostGoals=models.IntegerField()
    matchPlayed=models.IntegerField()
    teamID=models.ForeignKey(Team)
    leagueID=models.ForeignKey(League)

class PlayerStats(models.Model):
    matchID=models.ForeignKey(Match)
    teamID=models.ForeignKey(Team)
    playerID=models.ForeignKey(Player)
    isSubstitution=models.BooleanField()
    entryTime=models.IntegerField()
    shoots=models.IntegerField()
    shootsOnTarget=models.IntegerField()
    fouls=models.IntegerField()
    offsides=models.IntegerField()
class League_Team_Player(models.Model):
    leagueID=models.ForeignKey(League)
    teamID=models.ForeignKey(Team)
    playerID=models.ForeignKey(Player)
