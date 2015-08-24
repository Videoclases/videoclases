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
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
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

class CrearCursoFormView(FormView):
    template_name = 'crear-curso.html'
    form_class = CrearCursoSubirArchivoForm
    success_url = '/profesor/'

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
        try:
            sheet = data['Sheet1']
        except:
            sheet = data['Hoja 1']
        # Check if alumnos data is complete
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
        return JsonResponse(result_dict)

    def form_valid(self, form):
        result_dict = {}
        tarea = form.save(commit=False)
        tarea.profesor = self.request.user.profesor
        tarea.save()
        result_dict['id'] = tarea.id
        return JsonResponse(result_dict)

class CursoView(TemplateView):
    template_name = 'curso.html'

    def get_context_data(self, **kwargs):
        context = super(CursoView, self).get_context_data(**kwargs)
        curso = Curso.objects.get(id=kwargs['curso_id'])
        alumnos = curso.alumno_set.all()
        alumnos_array = []
        for alumno in alumnos:
            alumno_dict = {}
            alumno_dict['id'] = alumno.id
            alumno_dict['apellido'] = alumno.usuario.last_name
            alumno_dict['nombre'] = alumno.usuario.first_name
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
    alumnos = curso.alumno_set.all()
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

    def form_valid(self, form, *args, **kwargs):
        alumno = self.request.user.alumno
        videoclase = form.cleaned_data['videoclase']
        respuesta = form.cleaned_data['respuesta']
        try:
            instancia = RespuestasDeAlumnos.objects.get(alumno=alumno,
                videoclase=videoclase)
            instancia.respuesta = respuesta
            instancia.save()
        except:
            RespuestasDeAlumnos.objects.create(alumno=alumno, videoclase=videoclase,
                respuesta=respuesta).save()
        return super(EvaluarVideoclaseView, self).form_valid(form, *args, **kwargs)

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

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

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

class TareaDetalleView(UpdateView):
    template_name = 'tarea-detalle.html'
    form_class = EditarTareaForm
    success_url = reverse_lazy('profesor')
    model = Tarea

    @method_decorator(user_passes_test(in_profesores_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(TareaDetalleView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TareaDetalleView, self).get_context_data(**kwargs)
        tarea = Tarea.objects.get(id=self.kwargs['tarea_id'])
        context['cursos'] = self.request.user.profesor.cursos.all()
        context['tarea'] = tarea
        context['videoclases_recibidas'] = Grupo.objects.filter(tarea=tarea) \
                                .exclude(videoclase__video__isnull=True) \
                                .exclude(videoclase__video__exact='').count()
        return context

    def form_valid(self, form):
        self.object = self.get_object()
        if self.object.video:
            video = self.object.video
        else:
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
            return reverse('profesor')
        elif user.groups.filter(name='Alumnos').exists():
            return reverse('alumno')

    def get(self, request, *args, **kwargs):
        return super(IndexView, self).get(request, *args, **kwargs)
 
class LoginError(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(status=401)