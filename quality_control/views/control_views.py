from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView


def in_students_group(user):
    if user:
        return user.groups.filter(name='Alumnos').exists()
    return False


def in_teachers_group(user):
    if user:
        return user.groups.filter(name='Profesores').exists()
    return False


class NewControlView(TemplateView):
    template_name = 'new_control.html'

    def get_context_data(self, **kwargs):
        context = super(NewControlView, self).get_context_data(**kwargs)
        # form = CrearTareaForm()
        # context['crear_homework_form'] = form
        # context['courses'] = self.request.user.teacher.courses.filter(year=timezone.now().year)
        # context['homeworks'] = Homework.objects.filter(course__in=context['courses'])
        return context

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(NewControlView, self).dispatch(*args, **kwargs)
