# coding=utf-8
from django.db import models


class BooleanParameters(models.Model):
    description = models.CharField(max_length=256)
    value = models.BooleanField()

    def __str__(self):
        return self.description + ': ' + str(self.value)

    class Meta:
        verbose_name = 'Mis Parámetros'
        verbose_name_plural = 'Mis Parámetros'