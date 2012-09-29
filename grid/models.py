from django.db import models

from datetime import date, datetime, timedelta
from mechanize import Browser
import re

from grid.scoreboard_parser import ScoreboardParser

class Scraper(models.Model):
    run_at = models.DateTimeField()

    def scrape(self):
        # If our next scheduled scrape is in the future, we're done
        if self.run_at > datetime.now():
            return
        
        # If all games this week are final, we're done
        week = Week.objects.latest()
        all_done = True
        for game in week.game_set.all():
            if not game.is_final():
                all_done = False
                break
        if all_done:
            return
        
        # Pull in the scoreboard and parse all the tables with class 'data'
        # The parser will ignore non-scoreboard tables
        br = Browser()
        res = br.open(week.scoreboard_url)
        content = res.read()
        parser = ScoreboardParser()
        for table in re.findall('<table class="data.*?</table>', content):
            parser.feed(table)

        # After parsing each game we'll figure out when that games needs
        # to be scraped again, and the next scheduled run for the scraper
        # will be the soonest of all of those dates.  Start with a default
        # that's one day away.
        next_run = datetime.now() + timedelta(days=1)
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

            if time_left == "Final OT":
                time_left = "Final"
            try:
                game = week.game_set.get(away_team=away_team)
            except Game.DoesNotExist:
                print "Cannot find game with", away_team
                next
            game.away_score = away_score
            game.home_score = home_score
            game.time_left = time_left
            game.save()

            if game.in_progress():
                # If the game is in progress, we want to scrape it again right away
                next_run = min(next_run, datetime.now())
            elif not game.is_final():
                # If the game hasn't started yet, then we don't need to scrape it until it starts
                now = datetime.now()
                kickoff = datetime.strptime(game.time_left, "%I:%M %p")
                # Times are given in Eastern time, our server is Central, so adjust the hour
                gametime = datetime(year=now.year, month=now.month, day=now.day, hour=kickoff.hour-1, minute=kickoff.minute)
                # We don't know on which day a game is played, so if the time is in the past, assume the game happens
                # tomorrow.  Allow for 15 mins of wiggle room in case our clock and CBS' clock don't match.
                if gametime + timedelta(minutes=15) < datetime.now():
                    gametime += timedelta(days=1)

                next_run = min(next_run, gametime)
        self.run_at = next_run
        self.save()
        
class Week(models.Model):
    class Meta:
        get_latest_by = 'start_date'

    start_date = models.DateField('Date')
    number = models.IntegerField()
    scoreboard_url = models.CharField(max_length=255)

    def __unicode__(self):
        return "Week %d" % self.number
        
class Game(models.Model):
    class Meta:
        ordering = ["id"]

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

    def is_final(self):
        return self.time_left == "Final"

    def in_progress(self):
        if "QTR" in self.time_left:
            return True
        elif "OT" in self.time_left:
            return True
        elif "Halftime" in self.time_left:
            return True
        return False
