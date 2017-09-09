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
        # (u'Cumple muy parcialmente el criterio', 0.3),
        (u'Cumple parcialmente el criterio', 0.5),
        # (u'Cumple en su gran mayoria el criterio', 0.8),
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
    comments = models.TextField(default="",null=True,blank=True)
    videoclase = models.ForeignKey(VideoClase, related_name='evaluations')

    def __str__(self):
        return u'{0}, videoclase:{1}, {2}'.format(
            self.author.user.get_full_name(),
            self.videoclase.id,
            self.videoclase.homework.full_name()
        )