# coding=utf-8
from django.db import models

from videoclases.models.pedagogical_questions.pedagogical_questions import PedagogicalQuestions
from videoclases.models.pedagogical_questions.response import Response
from videoclases.models.student import Student


class PedagogicalQuestionsAnswers(models.Model):
    student = models.ForeignKey(Student)
    test = models.ForeignKey(PedagogicalQuestions)
    state_choices = [
        (1, u'Antes del envio de la tarea'),
        (2, u'Antes del la evaluación de videos'),
        (3, u'Después de la evaluación')
    ]

    state = models.IntegerField(choices=state_choices)
    response = models.ManyToManyField(Response)

    def get_info_state(self):
        choices = dict(self.state_choices)
        choice = self.test.get_state()
        if choice == 4:
            return "Finalizado"
        else:
            return choices[choice]

    @classmethod
    def get_states_dict(cls):
        return dict(cls.state_choices)

    def __unicode__(self):
        return u"{0} - {1} - {2}".format(self.test,self.student, self.get_info_state())