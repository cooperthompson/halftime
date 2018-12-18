from django.db import models

# modelst = Models for Templates


class LeagueTemplate(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'template_league'


class TeamTemplate(models.Model):
    number = models.IntegerField()
    league = models.ForeignKey('LeagueTemplate', related_name='teams')

    class Meta:
        managed = True
        db_table = 'template_team'


class GameTemplate(models.Model):
    league = models.ForeignKey('LeagueTemplate', on_delete=models.CASCADE)
    time = models.TimeField()
    field = models.ForeignKey('Field', on_delete=models.CASCADE)
    home_team = models.ForeignKey('TeamTemplate', on_delete=models.CASCADE)
    away_team = models.ForeignKey('TeamTemplate', on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'template_game'
