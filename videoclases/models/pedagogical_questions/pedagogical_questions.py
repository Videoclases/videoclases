# coding=utf-8
from collections import OrderedDict


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

    def export_as_xls(self):
        from pyexcel_xls import save_data
        import StringIO
        data = OrderedDict()
        list_data = list()
        list_data.append([])
        list_data.append([u"Título", self.title])
        list_data.append([u"Descripción (opcional)", self.description or ""])
        list_data.append([u"Duración", str(self.delta_time)])
        list_data.append([u"Pregunta", u"Alternativas"])

        for question in self.questions.all():
            question_data = list()
            question_data.append(question.question)
            for alternative in question.alternatives.all():
                question_data.append(alternative.response)
            list_data.append(question_data)
        data['Sheet1'] = list_data
        io = StringIO.StringIO()
        save_data(io, data,file_type='xls')
        return io
