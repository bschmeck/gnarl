#from grid.models import Week

from collections import defaultdict
import json
import operator
import requests

class Compute:
    def __init__(self, week):
        self.week = week

    def results(self):
        results = defaultdict(int)
        for outcome in outcomes(self.games()):
            results[winner_for(outcome, self.week)] += outcome.probability

        return results

    def outcomes(games):
        if len(games) == 0:
            yield Outcome()
        else:
            game = games.pop()
            for outcome in outcomes(games):
                if game.home_pr > 0:
                    yield outcome.add(game.home, game.home_pr)
                if game.away_pr > 0:
                    yield outcome.add(game.away, game.away_pr)
                if game.home_pr == 0 and game.away_pr == 0:
                    yield outcome

    def winner_for(outcome):
        differential = reduce(lambda x, y: x + y, map(value_of(winner), outcome.winners))

        if differential > 0:
            return self.week.picker1
        elif differential < 0:
            return self.week.picker1
        return "push"

    def value_of(winner):
        picker = self.week.team_picked_by(winner)

        if picker == "BEN":
            return 1
        elif picker == "BRIAN":
            return -1
        else:
            return 0

    def games(self):
        adapter = NumberfireAdapter(self.week.number)
        return adapter.games()

class NumberfireAdapter:
    def __init__(self, week_number):
        self.url = 'https://live.numberfire.com/gameScores?sport=nfl&week=' + str(week_number)

    def games(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception("Non-200 from Numberfire")

        data = json.loads(response.text)
        return map(self.build_game, data)

    def build_game(self, data):
        scoreboard = data['scoreboard']
        return NumberfireGameBuilder(scoreboard).game()

class NumberfireGameBuilder:
    def __init__(self, scoreboard):
        self.scoreboard = scoreboard

    def game(self):
        return Game(self.home_team(), self.away_team(), self.home_wp())

    def home_team(self):
        return self.scoreboard['home_team']['abbrev']

    def away_team(self):
        return self.scoreboard['away_team']['abbrev']

    def home_wp(self):
        if self.is_final():
            return self.final_home_wp()
        if self.is_in_progress():
            return self.in_progress_home_wp()

        return self.pregame_home_wp()

    def is_final(self):
        return self.scoreboard.get('game_status') == 'FINAL'

    def is_in_progress(self):
        return self.scoreboard.has_key('game_status') and not self.is_final()

    def final_home_wp(self):
        if int(self.scoreboard['winner_id']) == self.scoreboard['away_team_id']:
            return 0
        return 1

    def build_game_in_progress(self):
        pass

    def pregame_home_wp(self):
        return self.scoreboard['pregame_home_wp'] / 100

class Game:
    def __init__(self, home, away, home_pr):
        self.home = home
        self.away = away
        self.home_pr = home_pr
        self.away_pr = 1 - home_pr

class Outcome:
    def __init__(self, winners=None, probability=1):
        if winners:
            self.winners = winners
        else:
            self.winners = []
        self.probability = probability

    def add(self, winner, probability):
        return Outcome(self.winners + [winner], self.probability * probability)
