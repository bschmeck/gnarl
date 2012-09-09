from django.db import models

from datetime import date, datetime
from mechanize import Browser
import re

from grid.scoreboard_parser import ScoreboardParser

class Scraper(models.Model):
    run_at = models.DateTimeField()

    def scrape(self):
        week = Week.objects.latest()
        br = Browser()
        res = br.open(week.scoreboard_url)
        content = res.read()
        parser = ScoreboardParser()
        for table in re.findall('<table class="data.*?</table>', content):
            parser.feed(table)
        for parsed_game in parser.scores:
            if len(parsed_game) == 5:
                time_left = parsed_game[0]
                away_team = parsed_game[1]
                away_score = parsed_game[2]
                home_team = parsed_game[3]
                home_score = parsed_game[4]
            else:
                time_left = parsed_game[0]
                away_team = parsed_game[1]
                away_score = 0
                home_team = parsed_game[2]
                home_score = 0

            game = week.game_set.get(away_team=away_team)
            game.away_score = away_score
            game.home_score = home_score
            game.time_left = time_left
            game.save()
            
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
