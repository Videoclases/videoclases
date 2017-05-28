from django.db import models

from videoclases.models.student import Student
from videoclases.models.video_clase import VideoClase


class StudentEvaluations(models.Model):
    evaluations = (
        (u'No me gusta', -1),
        (u'Neutro', 0),
        (u'Me gusta', 1),
    )

    scores = [
        (u'No cumple el criterio', 0),
        (u'Cumple parcialmente el criterio', 0.5),
        (u'Cumple el criterio', 1)
    ]

    author = models.ForeignKey(Student)
    value = models.IntegerField(default=0)
    format = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    copyright = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    theme = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    pedagogical = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    rythm = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    originality = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    videoclase = models.ForeignKey(VideoClase, related_name='evaluations')

    def __unicode__(self):
        return 'Autor: ' + self.author.user.first_name + '. Valor: ' + str(self.value)