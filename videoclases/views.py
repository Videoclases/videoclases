#-*- coding: UTF-8 -*-

import codecs
import json
import os
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.validators import URLValidator
from django.db.models import Count, Q
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, UpdateView
from pyexcel_ods import get_data as ods_get_data
from pyexcel_xls import get_data as xls_get_data
from pyexcel_xlsx import get_data as xlsx_get_data
from videoclases.forms import *
from videoclases.models import *

SHOW_CORRECT_ANSWER = 'Mostrar alternativa correcta'

def in_alumnos_group(user):
    if user:
        return user.groups.filter(name='Alumnos').exists()
    return False

def in_profesores_group(user):
    if user:
        return user.groups.filter(name='Profesores').exists()
    return False

class AlumnoView(TemplateView):
    template_name = 'alumno.html'

    def get_context_data(self, **kwargs):
        context = super(AlumnoView, self).get_context_data(**kwargs)
        alumno = self.request.user.alumno
        grupos = Grupo.objects.filter(alumnos=alumno)
        for grupo in grupos:
            grupo.nota_final = NotasFinales.objects.get(alumno=alumno, grupo=grupo).ponderar_notas()
            grupo.videoclases_evaluadas = EvaluacionesDeAlumnos.objects \
                                            .filter(autor=alumno) \
                                            .filter(videoclase__grupo__tarea=grupo.tarea).count()
        context['grupos'] = grupos
        return context

    @method_decorator(user_passes_test(in_alumnos_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(AlumnoView, self).dispatch(*args, **kwargs)

class AsignarGrupoFormView(FormView):
    template_name = 'blank.html'
    form_class = AsignarGrupoForm

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(AsignarGrupoFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        grupos = json.loads(form.cleaned_data['grupos'])
        tarea = Tarea.objects.get(id=form.cleaned_data['tarea'])
        for numero in grupos:
            grupo, created = Grupo.objects.get_or_create(tarea=tarea, numero=int(numero))
            for alumno_id in grupos[numero]:
                grupo.alumnos.add(Alumno.objects.get(id=alumno_id))
            if created:
                for a in grupo.alumnos.all():
                    NotasFinales.objects.get_or_create(grupo=grupo, alumno=a)
                VideoClase.objects.get_or_create(grupo=grupo)
        result_dict = {}
        result_dict['success'] = True
        return JsonResponse(result_dict)

    def form_invalid(self, form):
        return super(AsignarGrupoFormView, self).form_invalid(form)

    def get(self, request, *args, **kwargs):
        return super(AsignarGrupoFormView, self).get(request, *args, **kwargs)

class BorrarCursoFormView(FormView):
    template_name = 'blank.html'
    form_class = BorrarCursoForm
    success_url = reverse_lazy('profesor')

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(BorrarCursoFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        curso = get_object_or_404(Curso, pk=self.kwargs['curso_id'])
        if curso not in self.request.user.profesor.cursos.all():
            messages.info(self.request, 'No tienes permisos para esta acción')
            return HttpResponseRedirect(reverse('profesor'))
        curso.delete()
        messages.info(self.request, 'El curso se ha eliminado exitosamente')
        return super(BorrarCursoFormView, self).form_valid(form, *args, **kwargs)

class BorrarTareaFormView(FormView):
    template_name = 'blank.html'
    form_class = BorrarTareaForm
    success_url = reverse_lazy('profesor')

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(BorrarTareaFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        tarea = Tarea.objects.get(id=form.cleaned_data['tarea'])
        tarea.delete()
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
            user.profesor.changed_password = True
            user.profesor.save()
            return reverse('profesor')
        elif user.groups.filter(name='Alumnos').exists():
            user.alumno.changed_password = True
            user.alumno.save()
            return reverse('alumno')

    def get_form(self, form_class):
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_initial(self):
        if in_alumnos_group(self.request.user):
            return {'email': self.request.user.email}

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(ChangePasswordView, self).get(self, request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(ChangePasswordView, self).post(self, request, *args, **kwargs)

class ChangeStudentPasswordView(FormView):
    template_name = 'cambiar-contrasena-alumno.html'
    form_class = ChangeStudentPasswordForm

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(ChangeStudentPasswordView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        form.save()
        messages.info(self.request, 'Clave cambiada exitosamente.')
        return super(ChangeStudentPasswordView, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        return super(ChangeStudentPasswordView, self).form_invalid(form, *args, **kwargs)

    def get_form(self, form_class):
        form = form_class(**self.get_form_kwargs())
        curso = Curso.objects.get(id=self.kwargs['curso_id'])
        form.fields['alumno'].queryset = curso.alumnos.all()
        return form

    def get_success_url(self):
        return reverse('profesor')

class ChangeStudentPasswordSelectCursoView(FormView):
    template_name = 'cambiar-contrasena-alumno-seleccionar-curso.html'
    form_class = ChangeStudentPasswordSelectCursoForm

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(ChangeStudentPasswordSelectCursoView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        self.kwargs['form'] = form
        return super(ChangeStudentPasswordSelectCursoView, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        return super(ChangeStudentPasswordSelectCursoView, self).form_invalid(form, *args, **kwargs)

    def get_form(self, form_class):
        form = form_class(**self.get_form_kwargs())
        form.fields['curso'].queryset = self.request.user.profesor.cursos.all()
        return form

    def get_success_url(self):
        curso = self.kwargs['form'].cleaned_data['curso']
        return reverse('change_student_password', kwargs={'curso_id':curso.id})

class CrearCursoFormView(FormView):
    template_name = 'crear-curso.html'
    form_class = CrearCursoSubirArchivoForm
    success_url = reverse_lazy('profesor')

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(CrearCursoFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        #(self, file, field_name, name, content_type, size, charset, content_type_extra=None)
        f = form.cleaned_data['file']
        path = settings.MEDIA_ROOT + '/' + f.name
        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        # Check file extension
        if f.name.endswith('.xlsx'):
            data = xlsx_get_data(path)
        elif f.name.endswith('.xls'):
            data = xls_get_data(path)
        elif f.name.endswith('.ods'):
            data = ods_get_data(path)
        else:
            os.remove(path)
            messages.info(self.request, 'El archivo debe ser formato XLS, XLSX u ODS.')
            return HttpResponseRedirect(reverse('crear_curso'))
        # assumes first sheet has info
        key, sheet = data.popitem()
        for i in range(1,len(sheet)):
            alumno_array = sheet[i]
            complete = True
            complete &= alumno_array[0] not in [None,'']
            complete &= alumno_array[1] not in [None,'']
            complete &= alumno_array[2] not in [None,'']
            complete &= alumno_array[3] not in [None,'']
            if not complete:
                os.remove(path)
                messages.info(self.request, 'El archivo no tiene toda la información de un alumno.')
                return HttpResponseRedirect(reverse('crear_curso'))
        # Create Curso
        curso, created = Curso.objects.get_or_create(colegio=self.request.user.profesor.colegio,
            nombre=form.cleaned_data['nombre'], anho=form.cleaned_data['anho'])
        self.request.user.profesor.cursos.add(curso)
        self.request.user.profesor.save()
        if created:
            # Create users and alumnos
            for i in range(1,len(sheet)):
                alumno_array = sheet[i]
                apellidos = unicode(alumno_array[0])
                nombre = unicode(alumno_array[1])
                username = unicode(alumno_array[2])
                password = unicode(alumno_array[3])
                if apellidos and nombre and username and password:
                    try:
                        user = User.objects.get(username=username)
                        user.alumno.cursos.add(curso)
                        user.alumno.save()
                    except:
                        user = User.objects.create_user(username=username, password=password, 
                            first_name=nombre, last_name=apellidos)
                        user.groups.add(Group.objects.get(name='Alumnos'))
                        a = Alumno.objects.create(usuario=user)
                        a.cursos.add(curso)
                        a.save()
        else:
            os.remove(path)
            messages.info(self.request, 'Ya existe un curso con ese nombre en este año.')
            return HttpResponseRedirect(reverse('crear_curso'))
        os.remove(path)
        messages.info(self.request, 'El curso se ha creado exitosamente')
        return HttpResponseRedirect(reverse('profesor'))

class CrearTareaView(TemplateView):
    template_name = 'crear-tarea.html'

    def get_context_data(self, **kwargs):
        context = super(CrearTareaView, self).get_context_data(**kwargs)
        form = CrearTareaForm()
        context['crear_tarea_form'] = form
        context['cursos'] = self.request.user.profesor.cursos.all()
        return context

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(CrearTareaView, self).dispatch(*args, **kwargs)

class CrearTareaFormView(FormView):
    template_name = 'blank.html'
    form_class = CrearTareaForm
    success_url = reverse_lazy('profesor')

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(CrearTareaFormView, self).dispatch(*args, **kwargs)

    def form_invalid(self, form):
        result_dict = {}
        result_dict['success'] = False
        result_dict['id'] = -1
        form_errors = []
        for field, errors in form.errors.items():
            print errors
            for error in errors:
                form_errors.append(error)
        result_dict['errors'] = form_errors
        return JsonResponse(result_dict)

    def form_valid(self, form):
        result_dict = {}
        tarea = form.save(commit=False)
        tarea.profesor = self.request.user.profesor
        tarea.save()
        result_dict['success'] = True
        result_dict['id'] = tarea.id
        result_dict['errors'] = []
        return JsonResponse(result_dict)

class CursoView(TemplateView):
    template_name = 'curso.html'

    def get_context_data(self, **kwargs):
        context = super(CursoView, self).get_context_data(**kwargs)
        curso = Curso.objects.get(id=kwargs['curso_id'])
        alumnos = curso.alumnos.all()
        alumnos_array = []
        for alumno in alumnos:
            alumno_dict = {}
            alumno_dict['id'] = alumno.id
            alumno_dict['apellido'] = alumno.usuario.last_name
            alumno_dict['nombre'] = alumno.usuario.first_name
            alumno_dict['username'] = alumno.usuario.username
            alumno_dict['tareas_entregadas'] = alumno.grupo_set.exclude(videoclase__video__isnull=True) \
                                    .exclude(videoclase__video__exact='').count()
            alumno_dict['tareas_pendientes'] = alumno.grupo_set \
                .filter(Q(videoclase__video='') | Q(videoclase__video__isnull=True)).count()
            alumno_dict['videoclases_respondidas'] = EvaluacionesDeAlumnos.objects \
                                            .filter(autor=alumno) \
                                            .filter(videoclase__grupo__tarea__curso=curso).count()
            alumnos_array.append(alumno_dict)
        context['alumnos'] = alumnos_array
        context['curso'] = curso
        return context

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(CursoView, self).dispatch(*args, **kwargs)

@user_passes_test(in_profesores_group, login_url='/')
def descargar_curso(request, curso_id):
    result_dict = {}
    curso = Curso.objects.get(id=curso_id)
    alumnos = curso.alumnos.all()
    curso_dict = {}
    curso_dict['id'] = curso.id
    curso_dict['nombre'] = curso.nombre
    alumnos_array = []
    for a in alumnos:
        alumno_dict = {}
        alumno_dict['id'] = a.id
        alumno_dict['apellido'] = a.usuario.last_name
        alumno_dict['nombre'] = a.usuario.first_name
        alumnos_array.append(alumno_dict)
    result_dict['alumnos'] = alumnos_array
    result_dict['curso'] = curso_dict
    return JsonResponse(result_dict)

@user_passes_test(in_profesores_group, login_url='/')
def descargar_grupos_tarea(request, tarea_id):
    result_dict = {}
    tarea = get_object_or_404(Tarea, pk=tarea_id)
    curso_dict = {}
    curso_dict['id'] = tarea.curso.id
    curso_dict['nombre'] = tarea.curso.nombre
    alumnos_array = []
    for g in tarea.grupos.all():
        for a in g.alumnos.all():
            alumno_dict = {}
            alumno_dict['id'] = a.id
            alumno_dict['apellido'] = a.usuario.last_name
            alumno_dict['nombre'] = a.usuario.first_name
            alumno_dict['grupo'] = g.numero
            alumno_dict['videoclase'] = g.videoclase.video not in [None,'']
            alumnos_array.append(alumno_dict)
    result_dict['alumnos'] = alumnos_array
    result_dict['curso'] = curso_dict
    return JsonResponse(result_dict)

class EditarAlumnoView(FormView):
    template_name = 'editar-alumno.html'
    form_class = EditarAlumnoForm

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EditarAlumnoView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        alumno = Alumno.objects.get(id=self.kwargs['alumno_id'])
        alumno.usuario.first_name = form.cleaned_data['first_name']
        alumno.usuario.last_name = form.cleaned_data['last_name']
        alumno.usuario.save()
        messages.info(self.request, 'El alumno ha sido editado exitosamente.')
        return super(EditarAlumnoView, self).form_valid(form, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        alumno = Alumno.objects.get(id=self.kwargs['alumno_id'])
        curso = Curso.objects.get(id=self.kwargs['curso_id'])
        if alumno not in curso.alumnos.all():
            raise Http404
        return super(EditarAlumnoView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EditarAlumnoView, self).get_context_data(**kwargs)
        alumno = Alumno.objects.get(id=self.kwargs['alumno_id'])
        context['alumno'] = alumno
        return context

    def get_initial(self):
        alumno = Alumno.objects.get(id=self.kwargs['alumno_id'])
        return {'first_name': alumno.usuario.first_name if alumno.usuario.first_name is not None else '',
                'last_name' : alumno.usuario.last_name  if alumno.usuario.last_name  is not None else '' }

    def get_success_url(self, *args, **kwargs):
        return reverse('editar_curso', kwargs={'curso_id': self.kwargs['curso_id']})

class EditarCursoView(TemplateView):
    template_name = 'editar-curso.html'

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EditarCursoView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EditarCursoView, self).get_context_data(**kwargs)
        curso = Curso.objects.get(id=kwargs['curso_id'])
        context['curso'] = curso
        return context

class EditarGrupoFormView(FormView):
    template_name = 'blank.html'
    form_class = AsignarGrupoForm

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EditarGrupoFormView, self).dispatch(*args, **kwargs)

    def all_alumnos_have_grupo(self, grupos, original_grupos):
        original_grupos_alumnos_count = 0
        grupos_alumnos_count = 0
        for g in original_grupos:
            original_grupos_alumnos_count += g.alumnos.all().count()
        for numero in grupos:
            for alumno_id in grupos[numero]:
                grupos_alumnos_count += 1
        return original_grupos_alumnos_count == grupos_alumnos_count

    def can_delete_grupo(self, grupo, tarea):
        can_delete = True
        for a in grupo.alumnos.all():
            nf = NotasFinales.objects.get(grupo__tarea=tarea, alumno=a)
            if nf.grupo == grupo:
                return False, 'raise'
        return True, None

    def can_edit_grupo(self, grupo, list_submitted_alumnos, list_contains_at_least_one_original):
        # if database grupo is the same than submitted grupo nothing happens
        if list(grupo.alumnos.all()) == list_submitted_alumnos:
            return False, None
        elif grupo.videoclase.video:
            # if database grupo has videoclase uploaded the grupo has to maintain
            # at least one original member
            if not list_contains_at_least_one_original:
                return False, 'raise'
            # if there is at least one original member, edit grupo
            else:
                return True, None
        # if there is no uploaded videoclase, all members can be changed
        else:
            return True, None

    def grupos_numbers_correct(self, grupos_json):
        numbers = range(1, len(grupos_json) + 1)
        for numero in grupos_json:
            numero_int = int(numero)
            try:
                numbers.remove(numero_int)
            except:
                pass
        return numbers == []

    @method_decorator(transaction.atomic)
    def form_valid(self, form):
        message = ''
        try:
            grupos = json.loads(form.cleaned_data['grupos'])
            if not self.grupos_numbers_correct(grupos):
                message = u'Los números de los grupos no son consecutivos. Revisa si hay algún error.'
                raise ValueError
            tarea = Tarea.objects.get(id=form.cleaned_data['tarea'])
            original_grupos = Grupo.objects.filter(tarea=tarea)
            # check if all alumnos from the original grupos have a grupo in submitted data
            if not self.all_alumnos_have_grupo(grupos, original_grupos):
                message = 'Datos incompletos, todos los alumnos deben tener grupo.'
                raise ValueError
            # check grupos from submitted info
            for numero in grupos:
                grupo_qs = Grupo.objects.filter(tarea=tarea, numero=int(numero))
                # check if grupo exists in database
                if grupo_qs.exists():
                    grupo = grupo_qs[0]
                    list_contains_at_least_one_original = False
                    # create list of alumnos from submitted info
                    list_submitted_alumnos = []
                    for alumno_id in grupos[numero]:
                        list_submitted_alumnos.append(Alumno.objects.get(id=alumno_id))
                        if grupo.alumnos.filter(id=alumno_id).exists():
                            list_contains_at_least_one_original = True
                    # check if can edit grupo
                    can_edit, exception = self.can_edit_grupo(grupo, list_submitted_alumnos, 
                        list_contains_at_least_one_original)
                    if exception == 'raise':
                        message = 'No se pueden cambiar todos los alumnos de un grupo ' + \
                                'que ya ha enviado videoclase: grupo número ' + str(grupo.numero)
                        raise ValueError
                    elif can_edit:
                        grupo.alumnos.clear()
                        for a in list_submitted_alumnos:
                            grupo.alumnos.add(a)
                            nf = NotasFinales.objects.get(grupo__tarea=tarea, alumno=a)
                            nf.grupo = grupo
                            nf.save()
                # if grupo does not exist, create grupo and add alumnos
                else:
                    grupo = Grupo.objects.create(tarea=tarea, numero=int(numero))
                    # create list of alumnos from submitted info
                    list_submitted_alumnos = []
                    for alumno_id in grupos[numero]:
                        list_submitted_alumnos.append(Alumno.objects.get(id=alumno_id))
                    for a in list_submitted_alumnos:
                        grupo.alumnos.add(a)
                    grupo.save()
                    for a in grupo.alumnos.all():
                        nf = NotasFinales.objects.get(grupo__tarea=tarea, alumno=a)
                        nf.grupo = grupo
                        nf.save()
                    VideoClase.objects.get_or_create(grupo=grupo)
            # check if there are grupos that were not in the uploaded info
            # first, create a list of grupos ids submitted
            list_submitted_grupo_ids = []
            for numero in grupos:
                list_submitted_grupo_ids.append(int(numero))
            # get grupo queryset for other grupos
            grupos_not_submitted = Grupo.objects.filter(tarea=tarea) \
                                                .exclude(numero__in=list_submitted_grupo_ids)
            for g in grupos_not_submitted:
                can_delete, exception = self.can_delete_grupo(g, tarea)
                if exception == 'raise':
                    message = 'No se puede eliminar el grupo ' + str(g.numero) + '.'
                    raise ValueError
                else:
                    g.delete()
            result_dict = {}
            result_dict['success'] = True
            return JsonResponse(result_dict)
        except ValueError:
            result_dict = {}
            result_dict['success'] = False
            result_dict['message'] = unicode(message)
            return JsonResponse(result_dict)

    def form_invalid(self, form):
        print form.errors
        return super(EditarGrupoFormView, self).form_invalid(form)

class EditarTareaView(UpdateView):
    template_name = 'editar-tarea.html'
    form_class = EditarTareaForm
    success_url = reverse_lazy('profesor')
    model = Tarea

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EditarTareaView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EditarTareaView, self).get_context_data(**kwargs)
        tarea = Tarea.objects.get(id=self.kwargs['tarea_id'])
        context['cursos'] = self.request.user.profesor.cursos.all()
        context['tarea'] = tarea
        context['videoclases_recibidas'] = Grupo.objects.filter(tarea=tarea) \
                                .exclude(videoclase__video__isnull=True) \
                                .exclude(videoclase__video__exact='').count()
        return context

    def form_valid(self, form):
        self.object = self.get_object()
        if self.object.video not in ['',None]:
            video = self.object.video
        else:
            video = form.cleaned_data['video']
        if form.cleaned_data['video'] == 'empty video':
            video = ''
        self.object = form.save(commit=False)
        self.object.video = video
        self.object.save()
        result_dict = {}
        result_dict['id'] = self.object.id
        return JsonResponse(result_dict)

    def get_object(self):
        obj = get_object_or_404(self.model, pk=self.kwargs['tarea_id'])
        return obj

class EnviarVideoclaseView(UpdateView):
    template_name = 'enviar-videoclase.html'
    form_class = EnviarVideoclaseForm
    model = VideoClase
    success_url = reverse_lazy('alumno')

    @method_decorator(user_passes_test(in_alumnos_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        obj = self.get_object(self, *args, **kwargs)
        if obj.grupo.tarea.get_estado() == 3:
            messages.info(self.request, 'El plazo para enviar la tarea ya ha terminado.')
            return HttpResponseRedirect(reverse('alumno'))
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
                kwargs={'tarea_id':self.kwargs['tarea_id']}))
        self.object.video = form.cleaned_data['video']
        self.object.pregunta = form.cleaned_data['pregunta']
        self.object.alternativa_correcta = form.cleaned_data['alternativa_correcta']
        self.object.alternativa_2 = form.cleaned_data['alternativa_2']
        self.object.alternativa_3 = form.cleaned_data['alternativa_3']
        self.object.alumnos_subida = timezone.now()
        self.object.save()
        messages.info(self.request, 'La VideoClase se ha enviado correctamente.')
        return super(EnviarVideoclaseView, self).form_valid(form)

    def get_object(self, *args, **kwargs):
        tarea = get_object_or_404(Tarea, pk=self.kwargs['tarea_id'])
        grupo = get_object_or_404(Grupo, alumnos=self.request.user.alumno, tarea=tarea)
        return grupo.videoclase

    def get_context_data(self, *args, **kwargs):
        context = super(EnviarVideoclaseView, self).get_context_data(**kwargs)
        context['videoclase'] = self.object
        return context

    def get_initial(self):
        return {'video': self.object.video if self.object.video is not None else '',
                'pregunta': self.object.pregunta if self.object.pregunta is not None else '',
                'alternativa_correcta': self.object.alternativa_correcta if self.object.alternativa_correcta is not None else '',
                'alternativa_2': self.object.alternativa_2 if self.object.alternativa_2 is not None else '',
                'alternativa_3': self.object.alternativa_3 if self.object.alternativa_3 is not None else ''}

class EvaluacionesDeAlumnosFormView(UpdateView):
    template_name = 'blank.html'
    form_class = EvaluacionesDeAlumnosForm
    success_url = reverse_lazy('profesor')
    model = EvaluacionesDeAlumnos

    @method_decorator(user_passes_test(in_alumnos_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EvaluacionesDeAlumnosFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.autor = self.request.user.alumno
        self.object.save()
        result_dict = {}
        result_dict['valor'] = form.cleaned_data['valor']
        return JsonResponse(result_dict)

class EvaluarVideoclaseView(FormView):
    template_name = 'evaluar.html'
    form_class = RespuestasDeAlumnosForm

    @method_decorator(user_passes_test(in_alumnos_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        tarea = get_object_or_404(Tarea, pk=self.kwargs['tarea_id'])
        grupo = get_object_or_404(Grupo, alumnos=self.request.user.alumno, tarea=tarea)
        if tarea.get_estado() != 2:
            messages.info(self.request, u'Esta tarea no está en período de evaluación.')
            return HttpResponseRedirect(reverse('alumno'))
        context = self.get_context_data(*args, **kwargs)
        if context['redirect']:
            messages.info(self.request, u'Ya contestaste las VideoClases de todos tus compañeros')
            return HttpResponseRedirect(reverse('alumno'))
        return super(EvaluarVideoclaseView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        tarea = get_object_or_404(Tarea, pk=self.kwargs['tarea_id'])
        grupo = get_object_or_404(Grupo, alumnos=self.request.user.alumno, tarea=tarea)
        return super(EvaluarVideoclaseView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(EvaluarVideoclaseView, self).get_context_data(**kwargs)
        tarea = get_object_or_404(Tarea, pk=self.kwargs['tarea_id'])
        alumno = self.request.user.alumno
        grupo_alumno = get_object_or_404(Grupo, alumnos=alumno, tarea=tarea)
        grupos = Grupo.objects.filter(tarea=tarea).exclude(id=grupo_alumno.id) \
                      .exclude(videoclase__video__isnull=True) \
                      .exclude(videoclase__video__exact='') \
                      .exclude(videoclase__respuestas__alumno=alumno) \
                      .annotate(revisiones=Count('videoclase__respuestas')) \
                      .order_by('revisiones','?')
        grupo = grupos[0] if grupos.exists() else None
        if grupo:
            alternativas = [grupo.videoclase.alternativa_correcta, 
                            grupo.videoclase.alternativa_2, 
                            grupo.videoclase.alternativa_3]
            random.shuffle(alternativas)
            evaluacion, created = EvaluacionesDeAlumnos.objects.get_or_create(autor=alumno, 
                                                                              videoclase=grupo.videoclase)
            context['grupo'] = grupo
            context['alternativas'] = alternativas
            context['evaluacion'] = evaluacion
            context['redirect'] = False
        else:
            context['redirect'] = True
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse('evaluar_videoclase', kwargs={'tarea_id': self.kwargs['tarea_id']})

class EvaluarVideoclaseFormView(FormView):
    template_name = 'blank.html'
    form_class = RespuestasDeAlumnosForm

    @method_decorator(user_passes_test(in_alumnos_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(EvaluarVideoclaseFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        alumno = self.request.user.alumno
        videoclase = form.cleaned_data['videoclase']
        respuesta = form.cleaned_data['respuesta']
        result_dict = {}
        result_dict['success'] = True
        show_correct_answer = BooleanParameters.objects.get(description=SHOW_CORRECT_ANSWER).value
        result_dict['show_correct_answer'] = show_correct_answer
        try:
            instancia = RespuestasDeAlumnos.objects.get(alumno=alumno,
                videoclase=videoclase)
            instancia.respuesta = respuesta
            instancia.save()
            if show_correct_answer:
                result_dict['correct_answer'] = videoclase.alternativa_correcta
                result_dict['is_correct'] = instancia.is_correct()
        except:
            RespuestasDeAlumnos.objects.create(alumno=alumno,
                videoclase=videoclase, respuesta=respuesta).save()
            instancia = RespuestasDeAlumnos.objects.get(alumno=alumno,
                videoclase=videoclase, respuesta=respuesta)
            if show_correct_answer:
                result_dict['correct_answer'] = videoclase.alternativa_correcta
                result_dict['is_correct'] = instancia.is_correct()
        return JsonResponse(result_dict)

    def form_invalid(self, form):
        print form.errors
        result_dict = {}
        return JsonResponse(result_dict)

class IndexView(FormView):
    template_name = 'index.html'
    form_class = AuthenticationForm

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
            if user.profesor.changed_password:
                return reverse('profesor')
            else:
                return reverse('change_password')
        elif user.groups.filter(name='Alumnos').exists():
            if user.alumno.changed_password:
                return reverse('alumno')
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
    template_name = 'profesor.html'

    def get_context_data(self, **kwargs):
        context = super(ProfesorView, self).get_context_data(**kwargs)
        current_year = timezone.now().year
        profesor = self.request.user.profesor
        context['tareas'] = Tarea.objects.filter(curso__profesor=profesor) \
                                         .filter(curso__anho=current_year)
        context['cursos_sin_tarea'] = profesor.cursos.filter(tarea=None)
        return context

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(ProfesorView, self).dispatch(*args, **kwargs)

class SubirNotaFormView(FormView):
    template_name = 'blank.html'
    form_class = SubirNotaForm
    success_url = '/profesor/'

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(SubirNotaFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        grupo = Grupo.objects.get(id=form.cleaned_data['grupo'])
        alumno = Alumno.objects.get(id=form.cleaned_data['alumno'])
        notas = NotasFinales.objects.get(grupo=grupo, alumno=alumno)
        notas.nota_profesor = form.cleaned_data['nota']
        notas.save()
        result_dict = {}
        return JsonResponse(result_dict)

    def form_invalid(self, form):
        result_dict = {}
        return JsonResponse(result_dict)

class VerVideoclaseView(TemplateView):
    template_name = 'alumno-ver-videoclase.html'

    def get_context_data(self, **kwargs):
        context = super(VerVideoclaseView, self).get_context_data(**kwargs)
        tarea = Tarea.objects.get(id=self.kwargs['tarea_id'])
        grupo = Grupo.objects.get(tarea=tarea, alumnos=self.request.user.alumno)
        context['grupo'] = grupo
        return context

    @method_decorator(user_passes_test(in_alumnos_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        tarea = Tarea.objects.get(id=self.kwargs['tarea_id'])
        if tarea.get_estado() != 3:
            return HttpResponseRedirect(reverse('alumno'))
        return super(VerVideoclaseView, self).dispatch(*args, **kwargs)

def videoclases(request):
    return render(request, 'videoclases.html')

class VideoclasesAlumnoView(TemplateView):
    template_name = 'videoclases-alumno.html'

    def get_context_data(self, **kwargs):
        context = super(VideoclasesAlumnoView, self).get_context_data(**kwargs)
        alumno = Alumno.objects.get(id=kwargs['alumno_id'])
        grupos = alumno.grupo_set.exclude(videoclase__video=None).exclude(videoclase__video__exact='')
        grupos_pendientes = alumno.grupo_set.filter(Q(videoclase__video='') | Q(videoclase__video__isnull=True))
        vmerge = grupos | grupos_pendientes
        vmerge.order_by('-id')
        context['alumno'] = alumno
        context['grupos'] = vmerge
        return context

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(VideoclasesAlumnoView, self).dispatch(*args, **kwargs)

class VideoclasesTareaView(TemplateView):
    template_name = 'videoclases-tarea.html'

    def get_context_data(self, **kwargs):
        context = super(VideoclasesTareaView, self).get_context_data(**kwargs)
        tarea = get_object_or_404(Tarea, id=self.kwargs['tarea_id'])
        context['grupos'] = tarea.grupos.all()
        context['tarea'] = tarea
        return context

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(VideoclasesTareaView, self).dispatch(*args, **kwargs)

def ui(request):
    return render(request, 'zontal/ui.html')

def forms(request):
    return render(request, 'forms.html')
 
class LoginError(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(status=401)