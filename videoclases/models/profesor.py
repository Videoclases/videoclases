from django.contrib.auth.models import User
from django.db import models

from videoclases.models.colegio import Colegio
from videoclases.models.curso import Curso


class Profesor(models.Model):
    colegio = models.ForeignKey(Colegio)
    usuario = models.OneToOneField(User)
    cursos = models.ManyToManyField(Curso, blank=True)
    changed_password = models.BooleanField(default=False)

    def __unicode__(self):
        return self.usuario.first_name + ' ' + self.usuario.last_name