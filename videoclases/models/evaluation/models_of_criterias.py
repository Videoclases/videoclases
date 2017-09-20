# coding=utf-8
from django.db import models

from videoclases.models.evaluation.criterias_by_teacher import CriteriasByTeacher
from videoclases.models.evaluation.scala import Scala


class ModelsOfCriterias(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    criterias = models.ManyToManyField(CriteriasByTeacher)
    scala = models.ForeignKey(Scala)

    def __str__(self):
        if self.name:
            return str(self.name)
        else:
            return "Escala {0}, usando {1} conjunto de criterio/os".format(self.scala,self.criterias.count())

    class Meta:
        verbose_name = 'Módelo de evaluación'
        verbose_name_plural = 'Módelo de evaluaciones'
