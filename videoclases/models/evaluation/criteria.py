# coding=utf-8
from django.db import models


class Criteria(models.Model):
    value = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return str(self.value)

    class Meta:
        verbose_name = 'Criterios'
        verbose_name_plural = 'Criterios'
