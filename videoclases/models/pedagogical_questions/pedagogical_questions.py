from django.db import models

from videoclases.models.homework import Homework
from videoclases.models.pedagogical_questions.question import Question


class PedagogicalQuestions(models.Model):
    homework = models.OneToOneField(Homework)
    title = models.CharField(max_length=255)
    questions = models.ManyToManyField(Question, related_name='pedagogical_questions')
    delta_time = models.DurationField()
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.title
