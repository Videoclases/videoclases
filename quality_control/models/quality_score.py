# coding=utf-8
from django.db import models

from videoclases.models.evaluation.criteria import Criteria
from videoclases.models.teacher import Teacher


class QualityScore(models.Model):
    field = models.CharField(max_length=200, null=True,blank=True)
    criteria = models.ForeignKey(Criteria, null=True, blank=True)
    score = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, null=True, blank=True)

    def __str__(self):
        if self.criteria:
            return "{0}: {1}".format(self.criteria, self.score)
        return "{0}: {1}".format(
            self.field,
            self.score
        )
