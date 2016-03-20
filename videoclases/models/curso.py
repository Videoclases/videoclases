from django.db import models

from videoclases.models.colegio import Colegio


class Curso(models.Model):
    colegio = models.ForeignKey(Colegio)
    nombre = models.CharField(max_length=256)
    anho = models.IntegerField(default=2015)

    def __unicode__(self):
        return self.nombre + ' ' + str(self.anho)