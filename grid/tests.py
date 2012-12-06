from django.utils import unittest

from game import Game

class GameTest(unittest.TestCase):
    def setUp(self):
        self.game_final = Game.new(time_left="Final")
        self.game_first_quarter = Game.new(time_left="14:15 1st QTR")
        self.game_halftime = Game.new(time_left="Halftime")
        self.game_overtime = Game.new(time_left="OT")
        self.game_not_started = Game.new(time_left="8:00 PM")

    def test_final_game_is_final(self):
        self.assertTrue(self.game_final.is_final())
        
    def test_final_game_not_in_progress(self):
        self.assertFalse(self.game_final.in_progress())

    def test_first_quarter_in_progress(self):
        self.assertTrue(self.game_first_quarter.in_progress())

    def test_halftime_in_progress(self):
        self.assertTrue(self.game_halftime.in_progress())

    def test_overtime_in_progress(self):
        self.assertTrue(self.game_overtime.in_progress())

    def test_not_started_not_in_progress(self):
        self.assertFalse(self.game_not_started.in_progress())
