# coding=utf-8
from django.db import models

from videoclases.models.evaluation.criteria import Criteria
from videoclases.models.teacher import Teacher


class CriteriasByTeacher(models.Model):
    name = models.CharField(max_length=150,null=True,blank=True)
    criterias = models.ManyToManyField(Criteria)
    teacher = models.ForeignKey(Teacher)

    def __str__(self):
        if self.name:
            return str(self.name)
        return "Listado creado por profesor(a) {0}".format(self.teacher)

    class Meta:
        verbose_name = 'Criterio de evaluación'
        verbose_name_plural = 'Criterios de evaluaciones'
