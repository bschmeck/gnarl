from django.utils import unittest

from week import Week

class WeekTest(unittest.TestCase):
    def test_all_games_final(self):
        week_final = Week.new()
        game_final1 = Game.new(time_left="Final", week=week_final1)
        game_final2 = Game.new(time_left="Final", week=week_final2)
        self.assertTrue(week_final.all_games_final())

        week_in_progress = Week.new()
        game_final3 = Game.new(time_left="Final", week=self.week_in_progress)
        game_in_progress = Game.new(time_left="Final", week=self.week_in_progress)
        self.assertFalse(week_in_progress.all_games_final())

