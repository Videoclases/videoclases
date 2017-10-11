# coding=utf-8
from collections import OrderedDict

from django.db import models

from videoclases.models.homework import Homework
from videoclases.models.pedagogical_questions.question import Question
from django.utils import timezone
from pyexcel_xls import save_data
from io import StringIO


class PedagogicalQuestions(models.Model):
    homework = models.OneToOneField(Homework)
    title = models.CharField(max_length=255)
    questions = models.ManyToManyField(Question, related_name='pedagogical_questions')
    delta_time = models.DurationField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def export_as_xls(self):
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

    def export_answer_as_xls(self):
        from videoclases.models.pedagogical_questions.pedagogical_questions_answers import PedagogicalQuestionsAnswers
        pq_answers = PedagogicalQuestionsAnswers.objects.filter(test=self)
        choices_states = PedagogicalQuestionsAnswers.get_states_dict()
        if len(pq_answers) > 0:
            data = OrderedDict()
            for i in choices_states.keys():
                list_data = list()
                answers_state = pq_answers.filter(state=i)
                if len(answers_state) > 0:
                    list_data.append([choices_states[i]])
                    list_data.append([])
                    label_questions = [u'']
                    responses = answers_state[0].response.all()
                    for r in responses:
                        label_questions.append(str(r.question))
                    list_data.append(label_questions)
                    for answer in answers_state:
                       student_responses = [str(answer.student.user.get_full_name())]
                       for r in answer.response.all():
                            student_responses.append(str(r.answer))
                       list_data.append(student_responses)

                if len(list_data) > 0:
                    data['Sheet{0}'.format(i)] = list_data
            io = StringIO.StringIO()
            save_data(io, data, file_type='xls')
            return io
        return None

    def get_state(self):
        today = timezone.datetime.date(timezone.datetime.today())
        if today <= self.homework.date_upload:
            return 1
        elif today <= self.homework.date_upload + self.delta_time and today <= self.homework.date_evaluation:
            return 2
        elif today >= self.homework.date_evaluation and today <= self.homework.date_evaluation + self.delta_time:
            return 3
        else:
            return 4