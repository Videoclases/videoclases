from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from videoclases.models.curso import Curso


class Alumno(models.Model):
    usuario = models.OneToOneField(User)
    cursos = models.ManyToManyField(Curso, related_name='alumnos')
    changed_password = models.BooleanField(default=False)

    def curso_actual(self):
        curso_qs = self.cursos.filter(anho=timezone.now().year)
        return curso_qs[0] if curso_qs.exists() else False

    def __unicode__(self):
        if self.curso_actual():
            return 'Curso: ' + self.curso_actual().nombre + ' ' + str(self.curso_actual().anho) + ' ' + \
                   self.usuario.get_full_name()
        return 'Sin cursos actualmente'