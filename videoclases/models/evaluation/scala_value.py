# coding=utf-8
from django.db import models


class ScalaValue(models.Model):
    name = models.CharField(max_length=150)
    value = models.IntegerField()

    def __str__(self):
        return str(self.value)

    class Meta:
        verbose_name = 'Valores de Escala'
        verbose_name_plural = 'Valores de Escalas'
