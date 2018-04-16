# coding=utf-8
from django.db import models

from videoclases.models.evaluation.criteria import Criteria


class CriteriaResponse(models.Model):
    value = models.DecimalField(max_digits=10, decimal_places=3)
    criteria = models.ForeignKey(Criteria)

    def __str__(self):
        return "{0}, valor: {1}".format(self.criteria, self.value)

    class Meta:
        verbose_name = 'Respuesta de Criterios'
        verbose_name_plural = 'Respuestas Criterios'
