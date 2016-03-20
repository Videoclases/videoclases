from django.db import models

from videoclases.models.alumno import Alumno
from videoclases.models.tarea import Tarea


class Grupo(models.Model):
    numero         = models.IntegerField()
    tarea          = models.ForeignKey(Tarea, related_name='grupos')
    alumnos        = models.ManyToManyField(Alumno)

    class Meta:
        unique_together = (('numero', 'tarea'),)

    def __unicode__(self):
        return 'Curso: ' + self.tarea.curso.nombre + '. Tarea: ' + \
        self.tarea.titulo + '. Grupo: ' + str(self.numero)