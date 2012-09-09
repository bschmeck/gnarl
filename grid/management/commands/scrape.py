from django.core.management.base import BaseCommand, CommandError

from gnarl.grid.models import Scraper

class Command(BaseCommand):
    help = 'Scrape NFL scores from CBS Sportsline'

    def handle(self, *args, **options):
        scraper = Scraper.objects.all()[0]
        if not scraper:
            raise CommandError("Could not find scraper.")
        scraper.scrape()

    
