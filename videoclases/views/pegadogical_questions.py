# coding=utf-8
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.http.response import HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView, DetailView

from videoclases.forms.forms import CrearTareaForm
from videoclases.forms.pedagogical_questions_form import PedagogicalQuestionsForm
from videoclases.forms.upload_pedagogical_questions_form import UploadPedagogicalQuestionsForm
from videoclases.models.course import Course
from videoclases.models.pedagogical_questions.alternative import Alternative
from videoclases.models.pedagogical_questions.pedagogical_questions import PedagogicalQuestions
from videoclases.models.pedagogical_questions.question import Question
from videoclases.views.views import in_teachers_group
import pyexcel as pe
import datetime


class ConceptualTestsView(TemplateView):
    template_name = 'new_conceptual_test.html'

    def get_context_data(self, **kwargs):
        context = super(ConceptualTestsView, self).get_context_data(**kwargs)
        form = CrearTareaForm()
        context['crear_homework_form'] = form
        context['courses'] = self.request.user.teacher.courses.all()
        return context

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(ConceptualTestsView, self).dispatch(*args, **kwargs)


class ConceptualTestsFormView(FormView):
    template_name = 'blank.html'
    form_class = PedagogicalQuestionsForm

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(ConceptualTestsFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        questions_data = self.request.POST.get('questions', None)
        import json
        questions_data = json.loads(questions_data)
        list_questions = []
        for question in questions_data:
            pedagogical_question = Question()
            pedagogical_question.question = question['title']
            list_alternatives = []
            for alternative in question['choices']:
                a = Alternative()
                a.response = alternative['value']
                a.save()
                list_alternatives.append(a)
            pedagogical_question.save()
            pedagogical_question.alternatives.add(*list_alternatives)
            pedagogical_question.save()
            list_questions.append(pedagogical_question)
        instance = form.save()
        instance.questions.add(*list_questions)
        instance.save()
        result_dict = dict()
        result_dict['success'] = True
        return JsonResponse(result_dict)

    def form_invalid(self, form):
        return JsonResponse(form.errors)


@user_passes_test(in_teachers_group, login_url='/')
def download_homeworks(request, course_id):
    result_dict = {}
    course = Course.objects.get(id=course_id)
    homeworks = course.course_homework.all()
    homeworks_array = []
    for a in homeworks:
        homework_dict = dict()
        homework_dict['id'] = a.id
        homework_dict['name'] = a.title
        try:
            homework_dict['has_pq'] = a.pedagogicalquestions is not None
        except Exception:
            homework_dict['has_pq'] = False
        homeworks_array.append(homework_dict)
    result_dict['homeworks'] = homeworks_array
    return JsonResponse(result_dict)


class DownloadPedagogicalQuestionAsExcel(DetailView):
    model = PedagogicalQuestions
    template_name = 'blank.html'

    def render_to_response(self, context, **response_kwargs):
        pq = self.get_object()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = \
            'attachment; filename=%s.xls' % slugify(pq.title)

        wb = pq.export_as_xls()
        response.write(wb.getvalue())
        return response

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(DownloadPedagogicalQuestionAsExcel, self).dispatch(*args, **kwargs)


class PedagogicalQuestionEditView(DetailView):

    model = PedagogicalQuestions
    template_name = 'edit_test.html'

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(PedagogicalQuestionEditView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PedagogicalQuestionEditView, self).get_context_data(**kwargs)
        pq = self.get_object()
        delta_time = pq.delta_time
        days = delta_time.days
        hours = delta_time.seconds / 3600
        min = (delta_time.seconds % 3600) / 60
        context['days'] = days
        context['hours'] = hours
        context['min'] = min
        context['courses'] = self.request.user.teacher.courses.all()
        context['homeworks'] = pq.homework.course.course_homework.all()
        return context

    def post(self, request, *args, **kwargs):
        import json
        instance = self.get_object()
        form = PedagogicalQuestionsForm(request.POST, instance=instance)
        if form.is_valid():
            questions_data = request.POST.get('questions', None)
            questions_data = json.loads(questions_data)
            list_questions = []
            for question in questions_data:
                pedagogical_question = Question()
                pedagogical_question.question = question['title']
                list_alternatives = []
                for alternative in question['choices']:
                    a = Alternative()
                    a.response = alternative['value']
                    a.save()
                    list_alternatives.append(a)
                pedagogical_question.save()
                pedagogical_question.alternatives.add(*list_alternatives)
                pedagogical_question.save()
                list_questions.append(pedagogical_question)

            questions = instance.questions.all()
            for q in questions:
                q.alternatives.all().delete()
            questions.delete()
            instance = form.save()
            instance.questions.add(*list_questions)
            instance.save()
            result_dict = dict()
            result_dict['success'] = True
        else:
            result_dict = {'errors':form.errors}
        return JsonResponse(result_dict)


class PedagogicalQuestionCreateView(FormView):
    template_name = 'upload_or_create_new_conceptual_test.html'
    form_class = UploadPedagogicalQuestionsForm

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(PedagogicalQuestionCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PedagogicalQuestionCreateView, self).get_context_data()
        context['courses'] = self.request.user.teacher.courses.all()
        context['form'] = self.get_form()
        context['kwargs'] = self.get_form_kwargs()
        return context

    def form_valid(self, form):
        file = form.files['file']
        content = file.read()
        result = pe.get_book(file_type="xls", file_content=content)
        data = result.to_dict()
        data = data.items()[0][1][1:]
        title = data[0][1]
        description = data[1][1]
        delta_time = data[2][1]
        days = hours = min = 0
        if delta_time.find("days"):
            days, rest_time = delta_time.split("days,")
        elif delta_time.find("day"):
            days, rest_time = delta_time.split("day,")
        else:
            rest_time = delta_time
        hours, min, sec = rest_time.split(":")
        days = int(days)
        hours = int(hours)
        min = int(min)
        try:
            delta_time = datetime.timedelta(
                days=days,
                hours=hours,
                minutes=min
            )
        except:
            messages.error(self.request, "Formato de la duración inválido")
            return self.render_to_response(self.get_context_data())
        homework = form.cleaned_data['homework']
        questions = data[4:]

        list_questions = []
        for question_data in questions:
            question_title = question_data.pop(0)
            list_alternatives = []
            for alternative in question_data:
                if alternative != "":
                    a = Alternative()
                    a.response = alternative
                    a.save()
                    list_alternatives.append(a)

            if question_title == '' or len(list_alternatives) == 0:
                messages.error(self.request,"Formato de preguntas inválido")
                return self.render_to_response(self.get_context_data())
            pedagogical_question = Question()
            pedagogical_question.question = question_title
            pedagogical_question.save()
            pedagogical_question.alternatives.add(*list_alternatives)
            pedagogical_question.save()
            list_questions.append(pedagogical_question)

        new_pedagogical_question = PedagogicalQuestions()
        new_pedagogical_question.title = title
        new_pedagogical_question.description = description
        new_pedagogical_question.delta_time = delta_time
        new_pedagogical_question.homework = homework
        new_pedagogical_question.save()
        new_pedagogical_question.questions.add(*list_questions)
        new_pedagogical_question.save()

        messages.success(self.request, "Test creado correctamente")
        return HttpResponseRedirect(reverse('teacher'))
