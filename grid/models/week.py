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
