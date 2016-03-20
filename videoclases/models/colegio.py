from django.db import models


class Colegio(models.Model):
    nombre = models.CharField(max_length=64)

    def __unicode__(self):
        return self.nombre