from django.core.management.base import BaseCommand, CommandError

import time

from gnarl.grid.models import Scraper

class Command(BaseCommand):
    help = 'Scrape NFL scores from CBS Sportsline'

    def handle(self, *args, **options):
        scraper = Scraper.objects.all()[0]
        if not scraper:
            raise CommandError("Could not find scraper.")

        # The cron job can only call us once a minute.  To scrape more frequently
        # we need to run the scraper multiple times when called by cron.
        scraper.scrape()
        time.sleep(20)
        scraper.scrape()
    
    
