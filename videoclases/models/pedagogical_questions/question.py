from django.db import models


class Question(models.Model):
    question = models.CharField(max_length=255, blank=True, null=True)
    alternative_1 = models.CharField(max_length=255, blank=True, null=True)
    alternative_2 = models.CharField(max_length=255, blank=True, null=True)
    alternative_3 = models.CharField(max_length=255, blank=True, null=True)
