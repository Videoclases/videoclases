# -*- coding: UTF-8 -*-

import json
import os
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from quality_control.models.quality_control import QualityControl
from videoclases.forms.authentication_form import CustomAutheticationForm
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, UpdateView, CreateView
from pyexcel_ods import get_data as ods_get_data
from pyexcel_xls import get_data as xls_get_data
from pyexcel_xlsx import get_data as xlsx_get_data

from videoclases.forms.forms import *
from videoclases.models.boolean_parameters import BooleanParameters
from videoclases.models.evaluation.models_of_criterias import ModelsOfCriterias
from videoclases.models.final_scores import FinalScores
from videoclases.models.groupofstudents import GroupOfStudents
from videoclases.models.pedagogical_questions.pedagogical_questions import PedagogicalQuestions
from videoclases.models.pedagogical_questions.pedagogical_questions_answers import PedagogicalQuestionsAnswers
from videoclases.models.student import Student
from videoclases.models.student_evaluations import StudentEvaluations
from videoclases.models.student_responses import StudentResponses
from videoclases.models.video_clase import VideoClase

SHOW_CORRECT_ANSWER = 'Mostrar alternativa correcta'


def in_students_group(user):
    if user:
        return user.groups.filter(name='Alumnos').exists()
    return False


def in_teachers_group(user):
    if user:
        return user.groups.filter(name='Profesores').exists()
    return False


class AlumnoView(TemplateView):
    template_name = 'student.html'

    def get_context_data(self, **kwargs):
        context = super(AlumnoView, self).get_context_data(**kwargs)
        student = self.request.user.student
        groups = GroupOfStudents.objects.filter(students=student)
        for group in groups:
            group.nota_final = FinalScores.objects.get(student=student, group=group).ponderar_notas()
            homework_base =group.homework
            homework =homework_base
            if homework.homework_to_evaluate is not None:
                homework = homework.homework_to_evaluate
            group.videoclases_evaluadas = StudentResponses.objects.filter(
                Q(videoclase__homework=homework) | Q(videoclase__homework=homework_base),
                student=student).count()
            control = QualityControl.objects.filter(homework=homework)
            control = control[0] if control.exists() else None
            if control:
                group.videoclases_evaluadas += control.list_items.filter(
                    videoclase__answers__student=student).count()

            try:
                group.pq_answer = PedagogicalQuestionsAnswers.objects.get(
                    student=student,test=group.homework.pedagogicalquestions,
                    state=group.homework.pedagogicalquestions.get_state())
            except:
                group.pq_answer = None

        context['groups'] = groups
        return context

    @method_decorator(user_passes_test(in_students_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(AlumnoView, self).dispatch(*args, **kwargs)


class AsignarGrupoFormView(FormView):
    template_name = 'blank.html'
    form_class = AsignarGrupoForm

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(AsignarGrupoFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        groups = json.loads(form.cleaned_data['groups'])
        homework = Homework.objects.get(id=form.cleaned_data['homework'])
        for number in groups:
            group, created = GroupOfStudents.objects.get_or_create(homework=homework, number=int(number))
            for student_id in groups[number]:
                group.students.add(Student.objects.get(id=student_id))
            if created:
                for a in group.students.all():
                    FinalScores.objects.get_or_create(group=group, student=a)
                VideoClase.objects.get_or_create(group=group)
        result_dict = {}
        result_dict['success'] = True
        return JsonResponse(result_dict)

    def form_invalid(self, form):
        return super(AsignarGrupoFormView, self).form_invalid(form)

    def get(self, request, *args, **kwargs):
        return super(AsignarGrupoFormView, self).get(request, *args, **kwargs)


class BorrarAlumnoView(TemplateView):
    template_name = 'blank.html'

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(BorrarAlumnoView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        student = Student.objects.get(id=self.kwargs['student_id'])
        course = Course.objects.get(id=self.kwargs['course_id'])
        if student not in course.students.all():
            messages.info(self.request, 'El alumno no corresponde a este curso.')
            return HttpResponseRedirect(reverse('teacher'))
        if course not in self.request.user.teacher.courses.all():
            messages.info(self.request, 'No tienes permisos para esta acción')
            return HttpResponseRedirect(reverse('teacher'))
        course.students.remove(student)
        messages.info(self.request, 'El alumno fue borrado del course exitosamente.')
        return HttpResponseRedirect(reverse('editar_course', kwargs={'course_id': course.id}))

    def get_success_url(self, *args, **kwargs):
        return reverse('editar_course', kwargs={'course_id': self.kwargs['course_id']})


class BorrarCursoFormView(FormView):
    template_name = 'blank.html'
    form_class = BorrarCursoForm
    success_url = reverse_lazy('teacher')

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(BorrarCursoFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs['course_id'])
        if course not in self.request.user.teacher.courses.all():
            messages.info(self.request, 'No tienes permisos para esta acción')
            return HttpResponseRedirect(reverse('teacher'))
        course.delete()
        messages.info(self.request, 'El curso se ha eliminado exitosamente')
        return super(BorrarCursoFormView, self).form_valid(form, *args, **kwargs)


class BorrarTareaFormView(FormView):
    template_name = 'blank.html'
    form_class = BorrarTareaForm
    success_url = reverse_lazy('teacher')

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(BorrarTareaFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        homework = Homework.objects.get(id=form.cleaned_data['homework'])
        homework.delete()
        messages.info(self.request, 'La tarea se ha eliminado exitosamente')
        return super(BorrarTareaFormView, self).form_valid(form, *args, **kwargs)


class ChangePasswordView(FormView):
    template_name = 'cambiar-contrasena.html'
    form_class = ChangePasswordForm

    def form_valid(self, form, *args, **kwargs):
        user = self.request.user
        if user.check_password(form.cleaned_data['old_password']):
            form.save()
            user = authenticate(username=self.request.user.username,
                                password=form.cleaned_data['new_password1'])
            login(self.request, user)
            messages.info(self.request, 'Tu contraseña fue cambiada exitosamente')
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseRedirect(reverse('change_password'))

    def form_invalid(self, form, *args, **kwargs):
        return super(ChangePasswordView, self).form_invalid(form, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.groups.filter(name='Profesores').exists():
            user.teacher.changed_password = True
            user.teacher.save()
            return reverse('teacher')
        elif user.groups.filter(name='Alumnos').exists():
            user.student.changed_password = True
            user.student.save()
            return reverse('student')

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_initial(self):
        if in_students_group(self.request.user):
            return {'email': self.request.user.email}

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(ChangePasswordView, self).get(self, request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(ChangePasswordView, self).post(self, request, *args, **kwargs)


class ChangeStudentPasswordView(FormView):
    template_name = 'cambiar-contrasena-student.html'
    form_class = ChangeStudentPasswordForm

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(ChangeStudentPasswordView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        form.save()
        messages.info(self.request, 'Clave cambiada exitosamente.')
        return super(ChangeStudentPasswordView, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        return super(ChangeStudentPasswordView, self).form_invalid(form, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())
        course = Course.objects.get(id=self.kwargs['course_id'])
        form.fields['student'].queryset = course.students.all()
        form.fields['student'].label = 'Alumno'
        return form

    def get_success_url(self):
        return reverse('teacher')


class ChangeStudentPasswordSelectCursoView(FormView):
    template_name = 'cambiar-contrasena-student-seleccionar-course.html'
    form_class = ChangeStudentPasswordSelectCursoForm

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(ChangeStudentPasswordSelectCursoView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        self.kwargs['form'] = form
        return super(ChangeStudentPasswordSelectCursoView, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        return super(ChangeStudentPasswordSelectCursoView, self).form_invalid(form, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())
        form.fields['course'].queryset = self.request.user.teacher.courses.all()
        form.fields['course'].label = 'Curso'
        return form

    def get_success_url(self):
        course = self.kwargs['form'].cleaned_data['course']
        return reverse('change_student_password', kwargs={'course_id': course.id})


class CrearCursoFormView(FormView):
    template_name = 'crear-course.html'
    form_class = CrearCursoSubirArchivoForm
    success_url = reverse_lazy('teacher')

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(CrearCursoFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        # (self, file, field_name, name, content_type, size, charset, content_type_extra=None)
        f = form.cleaned_data['file']
        f.name = f.name.encode('ascii', 'ignore').decode('ascii')
        path = settings.MEDIA_ROOT + '/' + f.name

        def save_file(f, path):
            with open(path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

        # Check file extension
        if f.name.endswith('.xlsx'):
            save_file(f, path)
            data = xlsx_get_data(path)
        elif f.name.endswith('.xls'):
            save_file(f, path)
            data = xls_get_data(path)
        elif f.name.endswith('.ods'):
            save_file(f, path)
            data = ods_get_data(path)
        else:
            messages.info(self.request, 'El archivo debe ser formato XLS, XLSX u ODS.')
            return HttpResponseRedirect(reverse('crear_course'))
        # assumes first sheet has info
        key, sheet = data.popitem()
        for i in range(1, len(sheet)):
            student_array = sheet[i]
            if len(student_array) == 0:
                continue
            complete = False
            if len(student_array) > 3:
                complete = True
                complete &= student_array[0] not in [None, '']
                complete &= student_array[1] not in [None, '']
                complete &= student_array[2] not in [None, '']
                complete &= student_array[3] not in [None, '']
            if not complete:
                try:
                    os.remove(path)
                except Exception:
                    print("Not possible delete path")
                messages.info(self.request, 'El archivo no tiene toda la información de un alumno.')
                return HttpResponseRedirect(reverse('crear_course'))
        # Create Course
        course, created = Course.objects.get_or_create(school=self.request.user.teacher.school,
                                                       name=form.cleaned_data['name'], year=form.cleaned_data['year'])
        self.request.user.teacher.courses.add(course)
        self.request.user.teacher.save()
        if created:
            # Create users and students
            for i in range(1, len(sheet)):
                student_array = sheet[i]
                if len(student_array) == 0:
                    continue
                apellidos = str(student_array[0])
                name = str(student_array[1])
                username = str(student_array[2])
                password = str(student_array[3])
                if apellidos and name and username and password:
                    try:
                        user = User.objects.get(username=username)
                        user.student.courses.add(course)
                        user.student.save()
                    except:
                        user = User.objects.create_user(username=username, password=password,
                                                        first_name=name, last_name=apellidos)
                        user.groups.add(Group.objects.get(name='Alumnos'))
                        a = Student.objects.create(user=user)
                        a.courses.add(course)
                        a.save()
        else:
            os.remove(path)
            messages.info(self.request, 'Ya existe un curso con ese nombre en este año.')
            return HttpResponseRedirect(reverse('crear_course'))
        os.remove(path)
        messages.info(self.request, 'El curso se ha creado exitosamente')
        return HttpResponseRedirect(reverse('teacher'))


class CrearTareaView(TemplateView):
    template_name = 'crear-homework.html'

    def get_context_data(self, **kwargs):
        context = super(CrearTareaView, self).get_context_data(**kwargs)
        form = CrearTareaForm()
        context['crear_homework_form'] = form
        teacher = self.request.user.teacher
        context['courses'] = teacher.courses.filter(year=timezone.now().year)
        context['previous_scalas'] = ModelsOfCriterias.objects.all(teacher__school=teacher.school)
        context['homeworks'] = Homework.objects.filter(course__in=context['courses'])
        return context

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(CrearTareaView, self).dispatch(*args, **kwargs)


class CrearTareaFormView(FormView):
    template_name = 'blank.html'
    form_class = CrearTareaForm
    success_url = reverse_lazy('teacher')

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(CrearTareaFormView, self).dispatch(*args, **kwargs)

    def form_invalid(self, form):
        result_dict = {}
        result_dict['success'] = False
        result_dict['id'] = -1
        form_errors = []
        for field, errors in form.errors.items():
            print(errors)
            for error in errors:
                form_errors.append(error)
        result_dict['errors'] = form_errors
        return JsonResponse(result_dict)

    def form_valid(self, form):
        result_dict = {}
        homework = form.save(commit=False)
        homework.teacher = self.request.user.teacher
        homework.save()
        result_dict['success'] = True
        result_dict['id'] = homework.id
        result_dict['errors'] = []
        return JsonResponse(result_dict)


class CursoView(TemplateView):
    template_name = 'course.html'

    def get_context_data(self, **kwargs):
        context = super(CursoView, self).get_context_data(**kwargs)
        course = Course.objects.get(id=kwargs['course_id'])
        students = course.students.all()
        students_array = []
        for student in students:
            student_dict = {}
            student_dict['id'] = student.id
            student_dict['last_name'] = student.user.last_name
            student_dict['first_name'] = student.user.first_name
            student_dict['username'] = student.user.username
            student_dict['homeworks_entregadas'] = student.groupofstudents_set.exclude(videoclase__video__isnull=True) \
                .exclude(videoclase__video__exact='').count()
            student_dict['homeworks_pendientes'] = student.groupofstudents_set \
                .filter(Q(videoclase__video='') | Q(videoclase__video__isnull=True)).count()
            student_dict['videoclases_respondidas'] = StudentEvaluations.objects \
                .filter(author=student) \
                .filter(videoclase__group__homework__course=course).count()
            students_array.append(student_dict)
        context['students'] = students_array
        context['course'] = course
        return context

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(CursoView, self).dispatch(*args, **kwargs)


@user_passes_test(in_teachers_group, login_url='/')
def descargar_course(request, course_id):
    result_dict = {}
    course = Course.objects.get(id=course_id)
    students = course.students.all()
    course_dict = {}
    course_dict['id'] = course.id
    course_dict['name'] = course.name
    students_array = []
    for a in students:
        student_dict = {}
        student_dict['id'] = a.id
        student_dict['last_name'] = a.user.last_name
        student_dict['first_name'] = a.user.first_name
        students_array.append(student_dict)
    result_dict['students'] = students_array
    result_dict['course'] = course_dict
    return JsonResponse(result_dict)


@user_passes_test(in_teachers_group, login_url='/')
def descargar_groups_homework(request, homework_id):
    result_dict = {}
    homework = get_object_or_404(Homework, pk=homework_id)
    course_dict = {}
    course_dict['id'] = homework.course.id
    course_dict['name'] = homework.course.name
    students_array = []
    for g in homework.groups.all():
        for a in g.students.all():
            student_dict = {}
            student_dict['id'] = a.id
            student_dict['last_name'] = a.user.last_name
            student_dict['first_name'] = a.user.first_name
            student_dict['group'] = g.number
            student_dict['videoclase'] = g.videoclase.video not in [None, '']
            students_array.append(student_dict)
    result_dict['students'] = students_array
    result_dict['course'] = course_dict
    return JsonResponse(result_dict)


class EditarAlumnoView(FormView):
    template_name = 'editar-student.html'
    form_class = EditarAlumnoForm

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EditarAlumnoView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        student = Student.objects.get(id=self.kwargs['student_id'])
        student.user.first_name = form.cleaned_data['first_name']
        student.user.last_name = form.cleaned_data['last_name']
        student.user.save()
        messages.info(self.request, 'El alumno ha sido editado exitosamente.')
        return super(EditarAlumnoView, self).form_valid(form, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        student = Student.objects.get(id=self.kwargs['student_id'])
        course = Course.objects.get(id=self.kwargs['course_id'])
        if student not in course.students.all():
            raise Http404
        return super(EditarAlumnoView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EditarAlumnoView, self).get_context_data(**kwargs)
        student = Student.objects.get(id=self.kwargs['student_id'])
        context['student'] = student
        return context

    def get_initial(self):
        student = Student.objects.get(id=self.kwargs['student_id'])
        return {'first_name': student.user.first_name if student.user.first_name is not None else '',
                'last_name': student.user.last_name if student.user.last_name is not None else ''}

    def get_success_url(self, *args, **kwargs):
        return reverse('editar_course', kwargs={'course_id': self.kwargs['course_id']})


class EditarCursoView(TemplateView):
    template_name = 'editar-course.html'

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EditarCursoView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EditarCursoView, self).get_context_data(**kwargs)
        course = Course.objects.get(id=kwargs['course_id'])
        context['course'] = course
        return context


class EditarGrupoFormView(FormView):
    template_name = 'blank.html'
    form_class = AsignarGrupoForm

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EditarGrupoFormView, self).dispatch(*args, **kwargs)

    def all_students_have_group(self, groups, original_groups):
        original_groups_students_count = 0
        groups_students_count = 0
        for g in original_groups:
            original_groups_students_count += g.students.all().count()
        for number in groups:
            for student_id in groups[number]:
                groups_students_count += 1
        return original_groups_students_count == groups_students_count

    def can_delete_group(self, group, homework):
        can_delete = True
        for a in group.students.all():
            nf = FinalScores.objects.get(group__homework=homework, student=a)
            if nf.group == group:
                return False, 'raise'
        return True, None

    def can_edit_group(self, group, list_submitted_students, list_contains_at_least_one_original):
        # if database group is the same than submitted group nothing happens
        if list(group.students.all()) == list_submitted_students:
            return False, None
        elif group.videoclase.video:
            # if database group has videoclase uploaded the group has to maintain
            # at least one original member
            if not list_contains_at_least_one_original:
                return False, 'raise'
            # if there is at least one original member, edit group
            else:
                return True, None
        # if there is no uploaded videoclase, all members can be changed
        else:
            return True, None

    def groups_numbers_correct(self, groups_json):
        numbers = list(range(1, len(groups_json) + 1))
        for number in groups_json:
            number_int = int(number)
            try:
                numbers.remove(number_int)
            except:
                pass
        return numbers == []

    @method_decorator(transaction.atomic)
    def form_valid(self, form):
        message = ''
        try:
            groups = json.loads(form.cleaned_data['groups'])
            if not self.groups_numbers_correct(groups):
                message = u'Los números de los groups no son consecutivos. Revisa si hay algún error.'
                raise ValueError
            homework = Homework.objects.get(id=form.cleaned_data['homework'])
            original_groups = GroupOfStudents.objects.filter(homework=homework)
            # check if all students from the original groups have a group in submitted data
            if not self.all_students_have_group(groups, original_groups):
                message = 'Datos incompletos, todos los alumnos deben tener grupo.'
                raise ValueError
            # check groups from submitted info
            for number in groups:
                group_qs = GroupOfStudents.objects.filter(homework=homework, number=int(number))
                # check if group exists in database
                if group_qs.exists():
                    group = group_qs[0]
                    list_contains_at_least_one_original = False
                    # create list of students from submitted info
                    list_submitted_students = []
                    for student_id in groups[number]:
                        list_submitted_students.append(Student.objects.get(id=student_id))
                        if group.students.filter(id=student_id).exists():
                            list_contains_at_least_one_original = True
                    # check if can edit group
                    can_edit, exception = self.can_edit_group(group, list_submitted_students,
                                                              list_contains_at_least_one_original)
                    if exception == 'raise':
                        message = 'No se pueden cambiar todos los alumnos de un group ' + \
                                  'que ya ha enviado videoclase: group número ' + str(group.number)
                        raise ValueError
                    elif can_edit:
                        group.students.clear()
                        for a in list_submitted_students:
                            group.students.add(a)
                            try:
                                nf = FinalScores.objects.get(group__homework=homework, student=a)
                            except Exception:
                                nf = FinalScores(student=a)
                            nf.group = group
                            nf.save()
                # if group does not exist, create group and add students
                else:
                    group = GroupOfStudents.objects.create(homework=homework, number=int(number))
                    # create list of students from submitted info
                    list_submitted_students = []
                    for student_id in groups[number]:
                        list_submitted_students.append(Student.objects.get(id=student_id))
                    for a in list_submitted_students:
                        group.students.add(a)
                    group.save()
                    for a in group.students.all():
                        nf = FinalScores.objects.get(group__homework=homework, student=a)
                        nf.group = group
                        nf.save()
                    VideoClase.objects.get_or_create(group=group)
            # check if there are groups that were not in the uploaded info
            # first, create a list of groups ids submitted
            list_submitted_group_ids = []
            for number in groups:
                list_submitted_group_ids.append(int(number))
            # get group queryset for other groups
            groups_not_submitted = GroupOfStudents.objects.filter(homework=homework) \
                .exclude(number__in=list_submitted_group_ids)
            for g in groups_not_submitted:
                can_delete, exception = self.can_delete_group(g, homework)
                if exception == 'raise':
                    message = 'No se puede eliminar el group ' + str(g.number) + '.'
                    raise ValueError
                else:
                    g.delete()
            result_dict = {}
            result_dict['success'] = True
            return JsonResponse(result_dict)
        except ValueError:
            result_dict = {}
            result_dict['success'] = False
            result_dict['message'] = str(message)
            return JsonResponse(result_dict)

    def form_invalid(self, form):
        print(form.errors)
        return super(EditarGrupoFormView, self).form_invalid(form)


class EditarTareaView(UpdateView):
    template_name = 'editar-homework.html'
    form_class = EditarTareaForm
    success_url = reverse_lazy('teacher')
    model = Homework

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EditarTareaView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EditarTareaView, self).get_context_data(**kwargs)
        homework = Homework.objects.get(id=self.kwargs['homework_id'])
        context['courses'] = self.request.user.teacher.courses.filter(year=timezone.now().year)
        context['homework'] = homework
        context['homeworks'] = Homework.objects.filter(course__in=context['courses']).exclude(id=homework.id)
        context['videoclases_recibidas'] = GroupOfStudents.objects.filter(homework=homework) \
            .exclude(videoclase__video__isnull=True) \
            .exclude(videoclase__video__exact='').count()
        return context

    def form_valid(self, form):
        self.object = self.get_object()
        self.object = form.save()
        result_dict = dict()
        result_dict['id'] = self.object.id
        return JsonResponse(result_dict)

    def get_object(self):
        obj = get_object_or_404(self.model, pk=self.kwargs['homework_id'])
        return obj


class EnviarVideoclaseView(UpdateView):
    template_name = 'enviar-videoclase.html'
    form_class = EnviarVideoclaseForm
    model = VideoClase
    success_url = reverse_lazy('student')

    @method_decorator(user_passes_test(in_students_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        obj = self.get_object(self, *args, **kwargs)
        if obj.group.homework.get_estado() == 3:
            messages.info(self.request, 'El plazo para enviar la homework ya ha terminado.')
            return HttpResponseRedirect(reverse('student'))
        return super(EnviarVideoclaseView, self).dispatch(*args, **kwargs)

    def form_invalid(self, form):
        return super(EnviarVideoclaseView, self).form_invalid(form)

    def form_valid(self, form):
        # check if video is a link
        validate = URLValidator()
        try:
            validate(form.cleaned_data['video'])
        except:
            messages.info(self.request, 'La VideoClase no corresponde a un link.')
            return HttpResponseRedirect(reverse('enviar_videoclase',
                                                kwargs={'homework_id': self.kwargs['homework_id']}))
        self.object.video = form.cleaned_data['video']
        self.object.question = form.cleaned_data['question']
        self.object.correct_alternative = form.cleaned_data['correct_alternative']
        self.object.alternative_2 = form.cleaned_data['alternative_2']
        self.object.alternative_3 = form.cleaned_data['alternative_3']
        self.object.upload_students = timezone.now()
        self.object.save()
        messages.info(self.request, 'La VideoClase se ha enviado correctamente.')
        return super(EnviarVideoclaseView, self).form_valid(form)

    def get_object(self, *args, **kwargs):
        homework = get_object_or_404(Homework, pk=self.kwargs['homework_id'])
        group = get_object_or_404(GroupOfStudents, students=self.request.user.student, homework=homework)
        return group.videoclase

    def get_context_data(self, *args, **kwargs):
        context = super(EnviarVideoclaseView, self).get_context_data(**kwargs)
        context['videoclase'] = self.object
        return context

    def get_initial(self):
        return {'video': self.object.video if self.object.video is not None else '',
                'question': self.object.question if self.object.question is not None else '',
                'correct_alternative': self.object.correct_alternative if self.object.correct_alternative is not None else '',
                'alternative_2': self.object.alternative_2 if self.object.alternative_2 is not None else '',
                'alternative_3': self.object.alternative_3 if self.object.alternative_3 is not None else ''}


class EvaluacionesDeAlumnosFormView(CreateView):
    template_name = 'blank.html'
    form_class = EvaluacionesDeAlumnosForm
    success_url = reverse_lazy('teacher')
    model = StudentEvaluations

    @method_decorator(user_passes_test(in_students_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EvaluacionesDeAlumnosFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        student = self.request.user.student
        evaluation, created = StudentEvaluations.objects.get_or_create(
            author=student,videoclase=form.cleaned_data['videoclase']
        )
        self.object = EvaluacionesDeAlumnosForm(self.request.POST,instance=evaluation)
        # self.object.author = self.request.user.student
        self.object.save()
        result_dict = {}
        result_dict['value'] = form.cleaned_data['value']
        return JsonResponse(result_dict)


class EvaluarVideoclaseView(FormView):
    template_name = 'evaluar.html'
    form_class = RespuestasDeAlumnosForm

    @method_decorator(user_passes_test(in_students_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        homework_base = get_object_or_404(Homework, pk=self.kwargs['homework_id'])
        homework = homework_base
        if homework_base.homework_to_evaluate is not None:
            homework = homework_base.homework_to_evaluate

        if homework.get_estado() != 2:
            messages.info(self.request, u'Esta tarea no está en período de evaluación.')
            return HttpResponseRedirect(reverse('student'))
        return super(EvaluarVideoclaseView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EvaluarVideoclaseView, self).get_context_data(**kwargs)
        context['homework_id'] = self.kwargs['homework_id']
        context['homework'] = get_object_or_404(Homework, pk=self.kwargs['homework_id'])
        homework_base = context['homework']
        homework = homework_base
        if homework_base.homework_to_evaluate is not None:
            homework = homework_base.homework_to_evaluate
        number_evaluations = \
            StudentEvaluations.objects.filter(
                Q(author=self.request.user.student),
                Q(videoclase__homework=homework) | Q(videoclase__homework=homework_base)).count()
        control = QualityControl.objects.filter(homework=homework)
        control = control[0] if control.exists() else None

        if control:
            number_evaluations += control.list_items.filter(videoclase__answers__student=self.request.user.student).count()

        context['number_evaluations'] = number_evaluations
        context['score'] = StudentEvaluations.scores
        return context

    def get(self, request, *args, **kwargs):
        homework = get_object_or_404(Homework, pk=self.kwargs['homework_id'])
        group = get_object_or_404(GroupOfStudents, students=self.request.user.student, homework=homework)
        return super(EvaluarVideoclaseView, self).get(self, request, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse('evaluar_videoclase', kwargs={'homework_id': self.kwargs['homework_id']})


class EvaluarVideoclaseFormView(FormView):
    template_name = 'blank.html'
    form_class = RespuestasDeAlumnosForm

    @method_decorator(user_passes_test(in_students_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EvaluarVideoclaseFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        student = self.request.user.student
        videoclase = form.cleaned_data['videoclase']
        answer = form.cleaned_data['answer']
        result_dict = {}
        result_dict['success'] = True
        show_correct_answer = BooleanParameters.objects.get(description=SHOW_CORRECT_ANSWER).value
        result_dict['show_correct_answer'] = show_correct_answer
        try:
            instancia = StudentResponses.objects.get(student=student,
                                                     videoclase=videoclase)
            instancia.answer = answer
            instancia.save()
            if show_correct_answer:
                result_dict['correct_answer'] = videoclase.correct_alternative
                result_dict['is_correct'] = instancia.is_correct()
        except:
            StudentResponses.objects.create(student=student,
                                            videoclase=videoclase, answer=answer).save()
            instancia = StudentResponses.objects.get(student=student,
                                                     videoclase=videoclase, answer=answer)
            if show_correct_answer:
                result_dict['correct_answer'] = videoclase.correct_alternative
                result_dict['is_correct'] = instancia.is_correct()
        return JsonResponse(result_dict)

    def form_invalid(self, form):
        print(form.errors)
        result_dict = {}
        return JsonResponse(result_dict)


class IndexView(FormView):
    template_name = 'index.html'
    form_class = CustomAutheticationForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=form.get_user(), password=password)
        if user is not None:
            if user.is_active:
                login(self.request, form.get_user())
                return HttpResponseRedirect(self.get_success_url(user))
        return super(IndexView, self).form_valid(form)

    def get_success_url(self, user):
        if user.groups.filter(name='Profesores').exists():
            if user.teacher.changed_password:
                return reverse('teacher')
            else:
                return reverse('change_password')
        elif user.groups.filter(name='Alumnos').exists():
            if user.student.changed_password:
                return reverse('student')
            else:
                return reverse('change_password')

    def get(self, request, *args, **kwargs):
        return super(IndexView, self).get(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


class PerfilView(TemplateView):
    template_name = 'perfil.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(PerfilView, self).get(request, *args, **kwargs)


class ProfesorView(TemplateView):
    template_name = 'teacher.html'

    def get_context_data(self, **kwargs):
        context = super(ProfesorView, self).get_context_data(**kwargs)
        current_year = timezone.now().year
        teacher = self.request.user.teacher
        context['homeworks'] = Homework.objects.filter(course__teacher=teacher) \
            .filter(course__year=current_year)
        context['courses_sin_homework'] = teacher.courses.filter(course_homework=None)
        return context

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(ProfesorView, self).dispatch(*args, **kwargs)


class SubirNotaFormView(FormView):
    template_name = 'blank.html'
    form_class = SubirNotaForm
    success_url = '/teacher/'

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(SubirNotaFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        group = GroupOfStudents.objects.get(id=form.cleaned_data['group'])
        student = Student.objects.get(id=form.cleaned_data['student'])
        notas = FinalScores.objects.get(group=group, student=student)
        notas.teacher_score = form.cleaned_data['nota']
        notas.save()
        result_dict = {}
        return JsonResponse(result_dict)

    def form_invalid(self, form):
        result_dict = {}
        return JsonResponse(result_dict)


class VerVideoclaseView(TemplateView):
    template_name = 'student-ver-videoclase.html'

    def get_context_data(self, **kwargs):
        context = super(VerVideoclaseView, self).get_context_data(**kwargs)
        homework = Homework.objects.get(id=self.kwargs['homework_id'])
        group = GroupOfStudents.objects.get(homework=homework, students=self.request.user.student)
        comments = StudentEvaluations.objects.filter(videoclase=group.videoclase,comments__isnull=False).exclude(
            comments__exact='').values('comments')
        context['comments'] = comments
        context['group'] = group
        return context

    @method_decorator(user_passes_test(in_students_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        homework = Homework.objects.get(id=self.kwargs['homework_id'])
        if homework.get_estado() != 3:
            return HttpResponseRedirect(reverse('student'))
        return super(VerVideoclaseView, self).dispatch(*args, **kwargs)


def videoclases(request):
    return render(request, 'videoclases.html')


class VideoclasesAlumnoView(TemplateView):
    template_name = 'videoclases-student.html'

    def get_context_data(self, **kwargs):
        context = super(VideoclasesAlumnoView, self).get_context_data(**kwargs)
        student = Student.objects.get(id=kwargs['student_id'])
        groups = student.groupofstudents_set.exclude(videoclase__video=None).exclude(videoclase__video__exact='')
        groups_pendientes = student.groupofstudents_set.filter(
            Q(videoclase__video='') | Q(videoclase__video__isnull=True))
        vmerge = groups | groups_pendientes
        vmerge.order_by('-id')
        context['student'] = student
        context['groups'] = vmerge
        return context

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(VideoclasesAlumnoView, self).dispatch(*args, **kwargs)


class VideoclasesTareaView(TemplateView):
    template_name = 'videoclases-homework.html'

    def get_context_data(self, **kwargs):
        context = super(VideoclasesTareaView, self).get_context_data(**kwargs)
        homework = get_object_or_404(Homework, id=self.kwargs['homework_id'])
        context['groups'] = homework.groups.all()
        context['homework'] = homework
        return context

    @method_decorator(user_passes_test(in_teachers_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(VideoclasesTareaView, self).dispatch(*args, **kwargs)


def ui(request):
    return render(request, 'zontal/ui.html')


def forms(request):
    return render(request, 'forms.html')


class LoginError(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(status=401)


