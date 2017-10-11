# coding=utf-8
from django.db import models


class ScalaValue(models.Model):
    name = models.CharField(max_length=150)
    value = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Valores de Escala'
        verbose_name_plural = 'Valores de Escalas'
