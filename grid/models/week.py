from django.db import models

class Week(models.Model):
    class Meta:
        app_label = 'grid'
        get_latest_by = 'start_date'
        
    start_date = models.DateField('Date')
    number = models.IntegerField()
    scoreboard_url = models.CharField(max_length=255)

    def __unicode__(self):
        return "Week %d" % self.number

    def all_games_final(self):
        for game in self.game_set.all():
            if not game.is_final():
                return False
        return True

    def team_picked_by(self, team):
        for game in self.game_set.all():
            if game.picked_team == team:
                return game.picker
