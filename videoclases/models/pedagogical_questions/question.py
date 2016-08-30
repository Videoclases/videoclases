from django.db import models

from videoclases.models.pedagogical_questions.alternative import Alternative


class Question(models.Model):
    question = models.CharField(max_length=255, blank=True, null=True)
    alternatives = models.ManyToManyField(Alternative, related_name='question_alternatives')
    correct = models.ForeignKey(Alternative, related_name='question_correct', blank=True, null=True)

    def __unicode__(self):
        return self.question
