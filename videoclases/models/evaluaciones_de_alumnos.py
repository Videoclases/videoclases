from django.db import models

from videoclases.models.alumno import Alumno
from videoclases.models.video_clase import VideoClase


class EvaluacionesDeAlumnos(models.Model):
    evaluaciones = (
        (u'No me gusta', -1),
        (u'Neutro', 0),
        (u'Me gusta', 1),
    )

    autor = models.ForeignKey(Alumno)
    valor = models.IntegerField(default=0)
    videoclase = models.ForeignKey(VideoClase, related_name='evaluaciones')

    def __unicode__(self):
        return 'Autor: ' + self.autor.usuario.first_name + '. Valor: ' + str(self.valor)