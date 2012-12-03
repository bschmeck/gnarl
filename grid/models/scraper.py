from django.db import models

from datetime import datetime, timedelta
from mechanize import Browser
import re
import urllib2

from grid.scoreboard_parser import ScoreboardParser

from game import Game
from week import Week

class Scraper(models.Model):
    class Meta:
        app_label = 'grid'
        
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
        try:
            br = Browser()
            res = br.open(week.scoreboard_url)
            content = res.read()
        except urllib2.URLError:
            print "Unable to connect to", week.scoreboard_url
            return
        
        parser = ScoreboardParser()
        for table in re.findall('<table class="lineScore.*?</table>', content):
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
            except Game.DoesNotExist:
                print "Cannot find game with", away_team
            
        self.run_at = next_run
        self.save()
        
