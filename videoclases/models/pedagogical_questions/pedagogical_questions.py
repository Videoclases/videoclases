from django.db import models

from videoclases.models.homework import Homework
from videoclases.models.pedagogical_questions.question import Question


class PedagogicalQuestions(models.Model):
    homework = models.OneToOneField(Homework)
    questions = models.ManyToManyField(Question, related_name='pedagogical_questions')
