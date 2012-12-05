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

    def time_to_scrape(self):
        # If our next scheduled scrape is in the future, we don't need to scrape
        return self.run_at <= datetime.now()

    # We need to run the scraper if:
    # 1. We have a week to scrape
    # 2. The scheduled scrape is not in the future
    # 3. The week has games which are not final
    def need_scrape(self):
        if not self.week:
            return False

        if not time_to_scrape():
            return False
            
        return not self.week.all_games_final()
        
    def scoreboard_content(self):
        try:
            br = Browser()
            res = br.open(week.scoreboard_url)
            content = res.read()
        except urllib2.URLError:
            print "Unable to connect to", week.scoreboard_url
            content = None
        return content        

    def scrape(self):
        self.week = Week.objects.latest()
        if not need_scrape():
            return

        # Pull in the scoreboard and parse all the tables with class 'data'
        # The parser will ignore non-scoreboard tables
        # Make sure we have content before parsing
        content = scoreboard_content()
        if not content:
            return
        parser = ScoreboardParser()
        for table in re.findall('<table class="lineScore.*?</table>', content):
            parser.feed(table)

        # After parsing each game we'll figure out when that games needs
        # to be scraped again, and the next scheduled run for the scraper
        # will be the soonest of all of those dates.  Start with a default
        # that's one day away.
        next_run = datetime.now() + timedelta(days=1)
        for parsed_game in parser.games:
            try:
                game = week.game_set.get(away_team=parsed_game.away_team)

                game.away_score = parsed_game.away_score
                game.home_score = parsed_game.home_score
                game.time_left = parsed_game.time_left
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
        
