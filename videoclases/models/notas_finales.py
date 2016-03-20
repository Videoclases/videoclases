from django.db import models

from videoclases.models.alumno import Alumno
from videoclases.models.grupo import Grupo


class NotasFinales(models.Model):
    grupo = models.ForeignKey(Grupo)
    alumno = models.ForeignKey(Alumno)
    nota_clase = models.FloatField(default=0, blank=True, null=True)
    nota_profesor = models.FloatField(default=0)

    def ponderar_notas(self):
        return self.nota_profesor

    def __unicode__(self):
        return 'Curso: ' + self.grupo.tarea.curso.nombre + '. Tarea: ' + \
        self.grupo.tarea.titulo + '. Grupo: ' + str(self.grupo.numero) + \
        '. Nota: ' + str(self.ponderar_notas())