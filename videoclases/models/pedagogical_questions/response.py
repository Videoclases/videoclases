from django.db import models

from videoclases.models.pedagogical_questions.alternative import Alternative
from videoclases.models.pedagogical_questions.question import Question


class Response(models.Model):
    question = models.ForeignKey(Question, related_name='response_question')
    answer = models.ForeignKey(Alternative, related_name='answer_question')
