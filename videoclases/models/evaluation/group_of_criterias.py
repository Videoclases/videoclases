# coding=utf-8
from django.db import models

from videoclases.models.evaluation.criteria import Criteria
from videoclases.models.evaluation.scala import Scala
from videoclases.models.teacher import Teacher


class GroupOfCriterias(models.Model):
    value = models.CharField(max_length=150)
    description = models.TextField()
    criterias = models.ManyToManyField(Criteria)
    scala = models.ForeignKey(Scala)
    teacher = models.ForeignKey(Teacher)

    def __unicode__(self):
        return str(self.value)

    class Meta:
        verbose_name = 'Módelo de evaluación'
        verbose_name_plural = 'Módelo de evaluaciones'
