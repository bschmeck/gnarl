from grid.models import Game, Scraper, Week
from django.contrib import admin

class GameAdmin(admin.ModelAdmin):
    exclude = ('home_score', 'away_score', 'time_left')
    
admin.site.register(Game, GameAdmin)
admin.site.register(Scraper)
admin.site.register(Week)
