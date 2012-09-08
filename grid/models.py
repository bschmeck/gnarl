from django.db import models

from datetime import date

class Week(models.Model):
    start_date = models.DateField('Date')
    number = models.IntegerField()
    scoreboard_url = models.CharField(max_length=255)

    def __unicode__(self):
        return "Week %d" % self.number

    class Meta:
        get_latest_by = 'start_date'
        
class Game(models.Model):
    PICKER_CHOICES = (
        ("BEN", "Ben"),
        ("BRIAN", "Brian"),
    )
    home_team = models.CharField(max_length=3)
    home_score = models.IntegerField()
    away_team = models.CharField(max_length=3)
    away_score = models.IntegerField()

    week = models.ForeignKey(Week)

    picked_team = models.CharField(max_length=3)
    picker = models.CharField(max_length=5, choices=PICKER_CHOICES)
    lock = models.BooleanField(default=False)
    anti_lock = models.BooleanField(default=False)

    time_left = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s @ %s - Week %d" % (self.away_team, self.home_team, self.week.number)
