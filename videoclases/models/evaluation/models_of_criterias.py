# coding=utf-8
from django.db import models

from videoclases.models.evaluation.criterias_by_teacher import CriteriasByTeacher
from videoclases.models.evaluation.scala import Scala
from videoclases.models.teacher import Teacher


class ModelsOfCriterias(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    criterias = models.ManyToManyField(CriteriasByTeacher)
    scala = models.ForeignKey(Scala)
    teacher = models.ForeignKey(Teacher)
    custom_cal = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Módelo de evaluación'
        verbose_name_plural = 'Módelo de evaluaciones'