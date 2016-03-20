from django.db import models

from videoclases.models.alumno import Alumno
from videoclases.models.video_clase import VideoClase


class RespuestasDeAlumnos(models.Model):
    videoclase = models.ForeignKey(VideoClase, related_name='respuestas')
    alumno = models.ForeignKey(Alumno)
    respuesta = models.CharField(max_length=100, blank=True, null=True)

    def is_correct(self):
        return self.respuesta == self.videoclase.alternativa_correcta

    def __unicode__(self):
        return 'Responde: ' + self.alumno.usuario.first_name + '. Respuesta: ' + unicode(self.respuesta) + \
        ' .Videoclase ' + str(self.videoclase.id) + ' ' + self.videoclase.grupo.tarea.titulo