from django.db import models

from videoclases.models.student import Student
from videoclases.models.video_clase import VideoClase


class StudentEvaluations(models.Model):
    evaluations = (
        (u'No me gusta', -1),
        (u'Neutro', 0),
        (u'Me gusta', 1),
    )

    author = models.ForeignKey(Student)
    value = models.IntegerField(default=0)
    videoclase = models.ForeignKey(VideoClase, related_name='evaluations')

    def __unicode__(self):
        return 'Autor: ' + self.author.user.first_name + '. Valor: ' + str(self.value)