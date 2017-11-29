from django.db import models

from videoclases.models.evaluation.criteria_response import CriteriaResponse
from videoclases.models.student import Student
from videoclases.models.video_clase import VideoClase


class StudentEvaluations(models.Model):
    evaluations = (
        (u'No me gusta', -1),
        (u'Neutro', 0),
        (u'Me gusta', 1),
    )


    # DEPRECATED
    scores = [
        (u'No cumple el criterio', 0),
        (u'Cumple muy parcialmente el criterio', 0.3),
        (u'Cumple parcialmente el criterio', 0.5),
        (u'Cumple en su gran mayoria el criterio', 0.8),
        (u'Cumple el criterio', 1)
    ]

    author = models.ForeignKey(Student)
    value = models.IntegerField(default=0)
    format = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    copyright = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    theme = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    pedagogical = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    rythm = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    originality = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    # END DEPRECATED

    criterias = models.ManyToManyField(CriteriaResponse, blank=True)
    comments = models.TextField(default="", null=True, blank=True)
    videoclase = models.ForeignKey(VideoClase, related_name='evaluations')

    def __str__(self):
        return u'{0}, videoclase:{1}, {2}'.format(
            self.author.user.get_full_name(),
            self.videoclase.id,
            self.videoclase.homework.full_name()
        )

    def get_evaluation(self):
        if self.criterias.count() > 0:
            result = list()
            for c in self.criterias.select_related('criteria'):
                result.append(
                    {'id': c.criteria.id, 'name': c.criteria.value, 'value': c.value}
                )
            return result
        return [
            {
                'id': 'originality',
                'name': 'Originalidad',
                'value': self.originality
            },
            {
              'id' : 'format',
                'name':'Formato',
                'value':self.format
            },
            {
              'id' : 'copyright',
                'name':'Licencias',
                'value':self.copyright
            },
            {
              'id' : 'theme',
                'name':'Tema',
                'value':self.theme
            },
            {
              'id' : 'pedagogical',
                'name': 'Pedagogía',
                'value': self.pedagogical
            },
            {
              'id' : 'rythm',
                'name':'Ritmo',
                'value':self.rythm
            },
        ]
