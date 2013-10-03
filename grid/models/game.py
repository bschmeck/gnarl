from django.db import models

from week import Week

class Game(models.Model):
    class Meta:
        app_label = 'grid'
        ordering = ["id"]

    PICKER_CHOICES = (
        ("BEN", "Ben"),
        ("BRIAN", "Brian"),
    )
    home_team = models.CharField(max_length=3)
    home_score = models.IntegerField(null=True, blank=True)
    away_team = models.CharField(max_length=3)
    away_score = models.IntegerField(null=True, blank=True)

    week = models.ForeignKey(Week)

    picked_team = models.CharField(max_length=3)
    picker = models.CharField(max_length=5, choices=PICKER_CHOICES)
    lock = models.BooleanField(default=False)
    anti_lock = models.BooleanField(default=False)

    time_left = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return "%s @ %s - Week %d" % (self.away_team, self.home_team, self.week.number)

    def is_final(self):
        return self.time_left == "Final"

    def in_progress(self):
        if "QTR" in self.time_left:
            return True
        elif "OT" in self.time_left:
            return True
        elif "Halftime" in self.time_left:
            return True
        return False
