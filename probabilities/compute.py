#from grid.models import Week

from collections import defaultdict
import operator

class Compute:
    def __init__(self, week):
        self.week = week

    def results(self):
        results = defaultdict(int)
        for outcome in outcomes(self.week.game_set):
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
        picker = self.week.picked_by(winner)

        if picker is None:
            return 0
        elif picker == self.week.picker1:
            return 1
        else:
            return -1

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
