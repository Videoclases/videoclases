# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models.query_utils import Q
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import FormView

from quality_control.models.quality_control import QualityControl
from videoclases.models.groupofstudents import GroupOfStudents
from videoclases.models.homework import Homework
from videoclases.models.student_evaluations import StudentEvaluations
from videoclases.models.video_clase import VideoClase
from videoclases.views.views import in_students_group,in_teachers_group


class HomeworkEvaluationsView(DetailView):
    template_name = 'homework_notes.html'
    model = Homework

    def get_context_data(self, **kwargs):
        context = super(HomeworkEvaluationsView, self).get_context_data(**kwargs)
        return context

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(HomeworkEvaluationsView, self).dispatch(*args, **kwargs)

class HomeworkEvaluationsTeacherView(DetailView):
    template_name = 'homework_teacher_evaluation.html'
    model = Homework

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(HomeworkEvaluationsTeacherView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HomeworkEvaluationsTeacherView, self).get_context_data(**kwargs)
        context['homework_id'] = self.object.pk
        context['homework'] = self.object
        homework_base = context['homework']
        homework = homework_base
        control = QualityControl.objects.filter(homework=homework)
        control = control[0] if control.exists() else None
        number_evaluations = 0

        context['number_evaluations'] = number_evaluations
        context['score'] = StudentEvaluations.scores
        return context

    def get(self, request, *args, **kwargs):
        return super(HomeworkEvaluationsTeacherView, self).get(self, request, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse('homework_evaluations_teacher', kwargs={'pk': self.kwargs['pk']})

