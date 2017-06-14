from django.db import models


class QualityScore(models.Model):
    field = models.CharField(max_length=200)
    score = models.FloatField()

    def __unicode__(self):
        return "{0}: {1}".format(
            self.field,
            self.score
        )