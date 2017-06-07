import random

from django.contrib.auth.decorators import user_passes_test
from django.db.models.aggregates import Count
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from videoclases.models.groupofstudents import GroupOfStudents
from videoclases.models.homework import Homework
from videoclases.models.student_evaluations import StudentEvaluations


def in_students_group(user):
    if user:
        return user.groups.filter(name='Alumnos').exists()
    return False

class GetVideoClaseView(TemplateView):
    template_name = 'blank.html'
    def get(self, request, *args, **kwargs):
        import ipdb
        ipdb.set_trace()
        result = dict()
        homework_base = get_object_or_404(Homework, pk=self.kwargs['homework_id'])
        homework = homework_base
        groups = GroupOfStudents.objects.filter(homework=homework)
        student = self.request.user.student
        if homework_base.homework_to_evaluate is not None:
            homework = homework_base.homework_to_evaluate
            groups = GroupOfStudents.objects.filter(homework=homework)
        else:
            group_student = get_object_or_404(GroupOfStudents, students=student, homework=homework)
            groups = groups.exclude(id=group_student.id)

        groups = groups \
            .exclude(videoclase__video__isnull=True) \
            .exclude(videoclase__video__exact='') \
            .exclude(videoclase__answers__student=student) \
            .annotate(revision=Count('videoclase__answers')) \
            .order_by('revision', '?')
        group = groups[0] if groups.exists() else None
        if group:
            alternativas = [group.videoclase.correct_alternative,
                            group.videoclase.alternative_2,
                            group.videoclase.alternative_3]
            random.shuffle(alternativas)
            evaluacion, created = StudentEvaluations.objects.get_or_create(author=student,
                                                                           videoclase=group.videoclase)
            result['group'] = group
            result['alternativas'] = alternativas
            result['evaluacion'] = evaluacion
            result['redirect'] = False
        else:
            result['redirect'] = True

        #TODO: chequear usuario, formato de result y enviar
        return JsonResponse(result)

    def get_context_data(self, **kwargs):
        context = super(GetVideoClaseView, self).get_context_data(**kwargs)

        return context

    @method_decorator(user_passes_test(in_students_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(GetVideoClaseView, self).dispatch(*args, **kwargs)
