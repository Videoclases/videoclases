# -*- coding: UTF-8 -*-
import json
from json.decoder import JSONDecodeError

from django.contrib.auth.decorators import user_passes_test
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from quality_control.models.quality_control import QualityControl
from quality_control.models.quality_item import QualityItem
from quality_control.models.quality_score import QualityScore
from videoclases.models.evaluation.criteria import Criteria
from videoclases.models.homework import Homework
from videoclases.models.student_evaluations import StudentEvaluations
from videoclases.models.video_clase import VideoClase
from videoclases.views.views import in_teachers_group


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
        # Fixme: update to real numbers
        number_evaluations = 0

        context['number_evaluations'] = number_evaluations
        context['score'] = StudentEvaluations.scores
        return context

    def get(self, request, *args, **kwargs):
        return super(HomeworkEvaluationsTeacherView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        criterias = request.POST.get('criteria', None)
        videoclase_id = int(request.POST.get('videoclase', None))
        videoclase = get_object_or_404(VideoClase, id=videoclase_id)
        if videoclase_id is None:
            return JsonResponse({'message': ['Videoclase no válida']}, status=500)
        messages = []
        if criterias:
            try:
                criterias = json.loads(criterias)
            except JSONDecodeError:
                return JsonResponse({'message': ['Formato de riterios de evaluación no válido']}, status=500)
            control = None
            try:
                control, created = QualityControl.objects.get_or_create(homework=self.get_object())
            except ValueError:
                control = QualityControl()
                control.save()
                control.homework.add(self.get_object())
            item, created = QualityItem.objects.get_or_create(
                videoclase=videoclase,
                teacher=request.user.teacher
            )
            if created:
                item.save()
                control.list_items.add(item)
            item.comments = request.POST.get('comments', None)
            item.save()
            for c in criterias:
                score, created = QualityScore.objects.get_or_create(
                    criteria=Criteria.objects.get(id=c['criteria']),
                    teacher=request.user.teacher
                )
                score.score = c['value']
                if created:
                    score.save()
                    item.score_check.add(score)
                score.save()
            return JsonResponse({})
        else:
            # not should be necessary, only for deprecated model
            pass

        return JsonResponse({'message': messages}, status=500)

    def get_success_url(self, *args, **kwargs):
        return reverse('homework_evaluations_teacher', kwargs={'pk': self.kwargs['pk']})

