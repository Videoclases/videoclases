import random

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView

from quality_control.models.quality_control import QualityControl
from videoclases.models.groupofstudents import GroupOfStudents
from videoclases.models.homework import Homework
from videoclases.models.video_clase import VideoClase
from videoclases.views.views import in_students_group, in_teachers_group


class GetVideoClaseView(DetailView):
    template_name = 'blank.html'
    model = Homework
    def get(self, request, *args, **kwargs):
        result = dict()
        homework_base = self.get_object()
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
        element_response = groups[0] if groups.exists() else None
        control = QualityControl.objects.filter(homework=homework)
        control = control[0] if control.exists() else None

        if control:
            evaluated_items = control.list_items.filter(videoclase__answers__student=student)
            # limit max evaluation of quality item to 5
            if evaluated_items.count() < 3:
                items = control.list_items.all() \
                    .exclude(videoclase__answers__student=student)
                item_to_evaluate = items[random.randint(0, items.count()-1)] if items.exists() else None
                if item_to_evaluate and element_response:
                    value_random = random.random()
                    # TODO: need to be a more smart filter
                    element_response = item_to_evaluate if value_random > 0.55 else element_response
                elif item_to_evaluate:
                    element_response = item_to_evaluate

        if element_response:
            alternativas = [element_response.videoclase.correct_alternative,
                            element_response.videoclase.alternative_2,
                            element_response.videoclase.alternative_3]
            random.shuffle(alternativas)
            result['video'] = element_response.videoclase.video
            result['question'] = element_response.videoclase.question
            result['videoclase_id'] = element_response.videoclase.pk
            result['alternativas'] = alternativas
            result['redirect'] = False
        else:
            result['redirect'] = True
        return JsonResponse(result)

    def get_context_data(self, **kwargs):
        context = super(GetVideoClaseView, self).get_context_data(**kwargs)
        return context

    @method_decorator(user_passes_test(in_students_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        obj = self.get_object()
        hw = Homework.objects.filter(id=obj.id,course__students=self.request.user.student)
        if hw.count() == 0:
            messages.info(self.request, 'No tienes permisos para evaluar esta tarea.')
            return HttpResponseRedirect(reverse('student'))
        return super(GetVideoClaseView, self).dispatch(*args, **kwargs)


class GetVideoClaseTeacherView(DetailView):
    template_name = 'blank.html'
    model = Homework

    def get(self, request, *args, **kwargs):
        result = dict()
        homework_base = self.get_object()
        homework = homework_base
        groups = GroupOfStudents.objects.filter(homework=homework)
        if homework_base.homework_to_evaluate is not None:
            homework = homework_base.homework_to_evaluate
            groups = GroupOfStudents.objects.filter(homework=homework)

        groups = groups \
            .exclude(videoclase__video__isnull=True) \
            .exclude(videoclase__video__exact='') \
            .annotate(revision=Count('videoclase__answers')) \
            .order_by('revision', '?')
        element_response = groups[0] if groups.exists() else None

        if element_response:
            alternativas = [element_response.videoclase.alternative_2,
                            element_response.videoclase.alternative_3]
            result['video'] = element_response.videoclase.video
            result['question'] = element_response.videoclase.question
            result['videoclase_id'] = element_response.videoclase.pk
            result['correctAnswer'] = element_response.videoclase.correct_alternative
            result['ohterChoices'] = alternativas
            result['redirect'] = False
        else:
            result['redirect'] = True
        return JsonResponse(result)

    def get_context_data(self, **kwargs):
        context = super(GetVideoClaseTeacherView, self).get_context_data(**kwargs)
        return context

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(GetVideoClaseTeacherView, self).dispatch(*args, **kwargs)


@user_passes_test(in_teachers_group, login_url='/')
def descargar_homework_evaluation(request, homework_id):
    homework = get_object_or_404(Homework, pk=homework_id)
    videoclases = VideoClase.objects.filter(homework=homework)
    data = []
    criterias_headers = []
    for v in videoclases:
        # import ipdb; ipdb.set_trace()
        if v.group:
            e = v.get_score_criterias() if homework.criterias.count() > 0 else v.get_multiple_criteria_score()
            for student in v.group.students.all():
                element = ["{0}, {1}".format(student.user.last_name, student.user.first_name)]
                element.extend([round(val, 3) for val in e.values()])
                criterias_headers = e.keys()
                data.append(element)

    headers = ['Estudiante']
    headers.extend(criterias_headers)
    results = {
        'headers': headers,
        'evaluations': data,
        'teacherEvaluations': 0
    }

    return JsonResponse(results, safe=False)
