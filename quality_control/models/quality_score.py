from django.db import models


class QualityScore(models.Model):
    field = models.CharField(max_length=200)
    score = models.FloatField()
