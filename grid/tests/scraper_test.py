from django.utils import unittest

from scraper import Scraper

class ScraperTest(unittest.TestCase):
    def setUp(self):
        self.week = Week.objects.create()
        self.game = Game.objects.create(week=self.week)
        self.scraper = Scraper.objects.create()

    def test_time_to_scrape(self):
        self.scraper.run_at = datetime.now() - timedelta(days=1)
        self.assertTrue(self.scraper.time_to_scrape())

        self.scraper.run_at = datetime.now() + timedelta(days=1)
        self.assertFalse(self.scraper.time_to_scrape())

    def test_need_scrape_without_week(self):
        self.scraper.week = None
        self.assertFalse(self.scraper.need_scrape())

    def test_need_scrape_not_time_to_scrape(self):
        self.scraper.week = week
        self.scraper.run_at = datetime.now() + timedelta(days=1)
        self.assertFalse(self.scraper.need_scrape())

    def test_need_scrape_all_games_final(self):
        self.scraper.week = week
        self.scraper.run_at = datetime.now() - timedelta(days=1)
        self.game.time_left = "Final"
        self.assertFalse(self.scraper.need_scrape())
        
    def test_need_scrape_not_all_games_final(self):
        self.scraper.week = week
        self.scraper.run_at = datetime.now() - timedelta(days=1)
        self.game.time_left = "OT"
        self.assertTrue(self.scraper.need_scrape())

