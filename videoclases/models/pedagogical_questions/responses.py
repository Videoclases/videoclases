from django.db import models

from videoclases.models.pedagogical_questions.alternative import Alternative
from videoclases.models.pedagogical_questions.pedagogical_questions import PedagogicalQuestions
from videoclases.models.student import Student


class Responses(models.Model):
    questions = models.ForeignKey(PedagogicalQuestions)
    student = models.ForeignKey(Student)
    answer = models.ManyToManyField(Alternative)
