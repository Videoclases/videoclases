#-*- coding: UTF-8 -*-

import os

from datetime import timedelta
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.db.models import Count, Q
from django.templatetags.static import static
from django.test import TestCase
from django.utils import timezone
from io import BytesIO
from videoclases.forms import *
from videoclases.models import *
from videoclases.views import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
todos_los_fixtures = ['devgroups', 'devusers', 'devcursos', 'devalumnos', 'devprofesores', 
    'devcolegio', 'devtareas', 'devgrupos', 'devvideoclasesevaluando', 'devnotasfinales',
    'devrespuestasdealumnos', 'devevaluacionesdealumnos']

class AlumnoTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_alumno_permissions(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('alumno'))
        self.assertEqual(response.status_code, 200)

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('alumno'))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('alumno'))
        self.assertEqual(response.status_code, 302)

    def test_estados_tarea(self):
        # fecha_subida = "2015-07-14"
        # fecha_evaluacion = "2015-07-15"
        # estado = 'Terminada'
        tarea = Tarea.objects.get(id=3)
        estados = dict(tarea.estados)
        self.assertEqual(tarea.get_estado(), estados.get('Terminada'))

        # fecha_subida = today - 1
        # fecha_evaluacion = today + 1
        # estado = 'Evaluando'
        today = timezone.datetime.date(timezone.datetime.now())
        tarea.fecha_evaluacion = today + timedelta(days=1)
        tarea.fecha_subida = today - timedelta(days=1)
        self.assertEqual(tarea.get_estado(), estados.get('Evaluando'))

        # fecha_subida = today + 1
        # fecha_evaluacion = today + 2
        # estado = 'Pendiente'
        tarea.fecha_evaluacion = today + timedelta(days=2)
        tarea.fecha_subida = today + timedelta(days=1)
        self.assertEqual(tarea.get_estado(), estados.get('Pendiente'))

    def test_lista_tareas_get_table(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('alumno'))
        alumno = Alumno.objects.get(usuario__username='alumno1')
        grupos = Grupo.objects.filter(alumnos=alumno)
        self.assertEqual(list(response.context['grupos']), list(grupos))

class CrearCursoTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('crear_curso'))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('crear_curso'))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('crear_curso'))
        self.assertEqual(response.status_code, 302)

    def crear_curso_form_correct(self, filename, content_type):
        # sheet has 2 alumnos
        # usernames dmunoz and anoram

        self.client.login(username='profe', password='profe')
        user = User.objects.get(username='profe')
        original_alumnos = Alumno.objects.all().count()
        path = BASE_DIR + '/project' + static(filename)
        upload_file = open(path, 'rb')
        #(self, file, field_name, name, content_type, size, charset, content_type_extra=None)
        imf = InMemoryUploadedFile(BytesIO(upload_file.read()), 'file', upload_file.name,
            content_type, os.path.getsize(path), None, {})
        file_dict = {'file': imf }
        form_data = {}
        form_data['nombre'] = 'Nombre'
        form_data['anho'] = 2015
        form_data['file'] = imf
        form = CrearCursoSubirArchivoForm(form_data, file_dict)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response redirect and message
        response = self.client.post(reverse('crear_curso'), form_data, follow=True)
        self.assertRedirects(response, reverse('profesor'))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'El curso se ha creado exitosamente')

        # assert valid creation of object
        curso = Curso.objects.filter(nombre='Nombre', anho=2015, colegio=user.profesor.colegio)
        self.assertTrue(curso.exists())
        self.assertEqual(curso.count(), 1)

        # assert valid creation of alumnos
        self.assertEqual(original_alumnos + 2, Alumno.objects.all().count())
        self.assertTrue(User.objects.filter(username='dmunoz').exists())
        self.assertTrue(User.objects.filter(username='anoram').exists())
        self.assertIsInstance(User.objects.get(username='dmunoz').alumno, Alumno)
        self.assertIsInstance(User.objects.get(username='anoram').alumno, Alumno)

    def test_crear_curso_form_correct_ods(self):
        self.crear_curso_form_correct(
            'test/correctSheet.ods',
            'application/vnd.oasis.opendocument.spreadsheet')

    def test_crear_curso_form_correct_xls(self):
        self.crear_curso_form_correct(
            'test/correctSheet.xls',
            'application/vnd.ms-excel')

    def test_crear_curso_form_correct_xlsx(self):
        self.crear_curso_form_correct(
            'test/correctSheet.xlsx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def crear_curso_form_incomplete(self, filename, content_type):
        # sheet has 2 alumnos
        # usernames dmunoz and anoram

        self.client.login(username='profe', password='profe')
        user = User.objects.get(username='profe')
        path = BASE_DIR + '/project' + static(filename)
        upload_file = open(path, 'rb')
        imf = InMemoryUploadedFile(BytesIO(upload_file.read()), 'file', upload_file.name,
            content_type, os.path.getsize(path), None, {})
        file_dict = {'file': imf }
        form_data = {}
        form_data['nombre'] = 'Nombre'
        form_data['anho'] = 2015
        form_data['file'] = imf
        form = CrearCursoSubirArchivoForm(form_data, file_dict)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response redirect and message
        response = self.client.post(reverse('crear_curso'), form_data, follow=True)
        self.assertRedirects(response, reverse('crear_curso'))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'El archivo no tiene toda la información de un alumno.')

    def test_crear_curso_form_incomplete_ods(self):
        self.crear_curso_form_incomplete(
            'test/incompleteSheet.ods',
            'application/vnd.oasis.opendocument.spreadsheet')

    def test_crear_curso_form_incomplete_xls(self):
        self.crear_curso_form_incomplete(
            'test/incompleteSheet.xls',
            'application/vnd.ms-excel')

    def test_crear_curso_form_incomplete_xlsx(self):
        self.crear_curso_form_incomplete(
            'test/incompleteSheet.xlsx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_crear_curso_form_wrong_extension(self):
        self.client.login(username='profe', password='profe')
        user = User.objects.get(username='profe')
        path = BASE_DIR + '/project' + static('test/image.png')
        upload_file = open(path, 'rb')
        imf = InMemoryUploadedFile(BytesIO(upload_file.read()), 'file', upload_file.name,
            'image/png', os.path.getsize(path), None, {})
        file_dict = {'file': imf }
        form_data = {}
        form_data['nombre'] = 'Nombre'
        form_data['anho'] = 2015
        form_data['file'] = imf
        form = CrearCursoSubirArchivoForm(form_data, file_dict)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response redirect and message
        response = self.client.post(reverse('crear_curso'), form_data, follow=True)
        self.assertRedirects(response, reverse('crear_curso'))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'El archivo debe ser formato XLS, XLSX u ODS.')

class CrearTareaTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('crear_tarea'))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('crear_tarea'))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('crear_tarea'))
        self.assertEqual(response.status_code, 302)

    def test_crear_tarea_get(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('crear_tarea'))
        user = User.objects.get(username='profe')
        cursos = user.profesor.cursos.all()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['cursos']), list(cursos))

    def test_crear_tarea_form(self):
        self.client.login(username='profe', password='profe')
        form_data = {}
        form_data['titulo'] = 'titulo'
        form_data['descripcion'] = 'descripcion'
        form_data['curso'] = 1
        form_data['revisiones'] = 1
        form_data['fecha_subida'] = '2015-07-16'
        form_data['fecha_evaluacion'] = '2015-07-20'
        form_data['video'] = 'https://www.youtube.com/watch?v=8a7sd82s'
        form = CrearTareaForm(form_data)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response
        response = self.client.post(reverse('crear_tarea_form'), form_data)
        self.assertEqual(response.status_code, 200)

        # assert valid creation of object
        new_tarea = Tarea.objects.get(titulo='titulo', descripcion='descripcion')
        self.assertEqual(new_tarea, Tarea.objects.latest('id'))
        self.assertEqual(new_tarea.video, u'https://www.youtube.com/embed/8a7sd82s')

    def test_asignar_grupo_form(self):
        self.client.login(username='profe', password='profe')
        form_data = {}
        form_data['grupos'] = '{"1":[34,37,38],"2":[31,39,40],"3":[33,35,36],"4":[32]}'
        form_data['tarea'] = 2
        form = AsignarGrupoForm(form_data)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response
        response = self.client.post(reverse('asignar_grupo_form'), form_data)
        self.assertEqual(response.status_code, 200)

        # assert valid creation of object
        alumnos = [Alumno.objects.get(id=34), Alumno.objects.get(id=37), Alumno.objects.get(id=38)]
        tarea = Tarea.objects.get(id=2)
        new_grupo = Grupo.objects.get(numero=1, tarea=tarea)
        self.assertEqual(list(new_grupo.alumnos.all()), list(alumnos))

        # assert valid creation of NotasFinales
        nf = NotasFinales.objects.get(grupo=new_grupo, alumno=Alumno.objects.get(id=34))

class CursoTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('curso', kwargs={'curso_id':1}))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('curso', kwargs={'curso_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('curso', kwargs={'curso_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_lista_cursos_get_table(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('curso', kwargs={'curso_id':1}))
        curso = Curso.objects.get(id=1)
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
        self.assertEqual(response.context['alumnos'], alumnos_array)
        self.assertEqual(response.context['curso'], curso)

class DescargarCursoTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('descargar_curso', kwargs={'curso_id':1}))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('descargar_curso', kwargs={'curso_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('descargar_curso', kwargs={'curso_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_json_download(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('descargar_curso', kwargs={'curso_id':1}))
        result_dict = {}
        curso = Curso.objects.get(id=1)
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
        self.assertJSONEqual(response.content,result_dict)

class DescargarGruposTareaTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('descargar_grupos_tarea', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('descargar_grupos_tarea', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('descargar_grupos_tarea', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_json_download(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('descargar_grupos_tarea', kwargs={'tarea_id':1}))
        result_dict = {}
        tarea = Tarea.objects.get(id=1)
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
        self.assertJSONEqual(response.content,result_dict)

class EnviarVideoclaseTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_alumno_has_tarea_permissions(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('enviar_videoclase', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 200)

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('enviar_videoclase', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('enviar_videoclase', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_alumno_does_not_have_tarea_permissions(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('enviar_videoclase', kwargs={'tarea_id':2}))
        self.assertEqual(response.status_code, 404)

    def test_alumno_tarea_does_not_exist_permissions(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('enviar_videoclase', kwargs={'tarea_id':1234567}))
        self.assertEqual(response.status_code, 404)

    def test_alumno_tarea_status_after_upload_date_before_evaluation_date(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('enviar_videoclase', kwargs={'tarea_id':10}))
        self.assertEqual(response.status_code, 200)

    def test_enviar_videoclase_get_data(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('enviar_videoclase', kwargs={'tarea_id':1}))
        tarea = Tarea.objects.get(id=1)
        user = User.objects.get(username='alumno1')
        videoclase = VideoClase.objects.get(grupo__alumnos=user.alumno, grupo__tarea=tarea)
        self.assertEqual(response.context['videoclase'], videoclase)

    def test_enviar_videoclase_form(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('enviar_videoclase', kwargs={'tarea_id':1}))
        user = User.objects.get(username='alumno1')
        form_data = {}
        form_data['video'] = 'https://www.youtube.com/watch?v=KMFOVSWn0mI'
        form_data['pregunta'] = u'¿1 + 2?'
        form_data['alternativa_correcta'] = '3'
        form_data['alternativa_2'] = '4'
        form_data['alternativa_3'] = '5'
        form = EnviarVideoclaseForm(form_data)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response
        response = self.client.post(reverse('enviar_videoclase', kwargs={'tarea_id':1}), form_data)
        self.assertEqual(response.status_code, 302)

        # assert valid creation of object
        link, success = VideoClase.process_youtube_default_link('https://www.youtube.com/watch?v=KMFOVSWn0mI')
        videoclase_enviada = VideoClase.objects.get(grupo__alumnos=user.alumno, video=link)
        latest_edited_videoclase = VideoClase.objects.all().order_by('-alumnos_subida')[0]
        self.assertEqual(videoclase_enviada, latest_edited_videoclase)

class EvaluarVideoclaseTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_alumno_has_tarea_permissions(self):
        self.client.login(username='alumno2', password='alumno')
        response = self.client.get(reverse('evaluar_videoclase', kwargs={'tarea_id':10}))
        self.assertEqual(response.status_code, 200)

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('evaluar_videoclase', kwargs={'tarea_id':10}))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('evaluar_videoclase', kwargs={'tarea_id':10}))
        self.assertEqual(response.status_code, 302)

    def test_alumno_does_not_have_tarea_permissions(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('evaluar_videoclase', kwargs={'tarea_id':2}))
        self.assertEqual(response.status_code, 404)

    def test_alumno_tarea_status_wrong_permissions(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('evaluar_videoclase', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 302)
        #self.assertEqual(response.context['tareas'], tareas)

    def test_alumno_tarea_does_not_exist_permissions(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('evaluar_videoclase', kwargs={'tarea_id':1234567}))
        self.assertEqual(response.status_code, 404)

    def test_template_get_random_group_data(self):
        self.client.login(username='alumno2', password='alumno')
        response = self.client.get(reverse('evaluar_videoclase', kwargs={'tarea_id':10}))
        tarea = Tarea.objects.get(id=10)
        user = User.objects.get(username='alumno2')

        # random group, with as less revisiones as possible
        grupo_alumno = Grupo.objects.get(alumnos=user.alumno, tarea=tarea)
        grupos = Grupo.objects.filter(tarea=tarea).exclude(id=grupo_alumno.id) \
                      .exclude(videoclase__video__isnull=True) \
                      .exclude(videoclase__video__exact='') \
                      .annotate(revisiones=Count('videoclase__respuestas')) \
                      .order_by('revisiones','?')
        response_grupo = response.context['grupo']
        self.assertIn(response_grupo, grupos)
        self.assertTrue(grupos[0].revisiones <= grupos.reverse()[0].revisiones)
        for i in range(0,20):
            self.assertNotEqual(response_grupo, grupo_alumno)

        # alternativas to pregunta in context
        alternativas = [response_grupo.videoclase.alternativa_correcta,
                        response_grupo.videoclase.alternativa_2,
                        response_grupo.videoclase.alternativa_3]
        alternativas.sort()
        response.context['alternativas'].sort()
        self.assertEqual(response.context['alternativas'], alternativas)

        # evaluaciondealumno
        evaluacion, created = EvaluacionesDeAlumnos.objects. \
                              get_or_create(autor=user.alumno, videoclase=response_grupo.videoclase)
        self.assertEqual(response.context['evaluacion'], evaluacion)

        # videoclase question not responded before
        self.assertFalse(response_grupo.videoclase.respuestas.filter(alumno=user.alumno))
        

    def test_evaluar_video_correct_data(self):
        self.client.login(username='alumno1', password='alumno')
        alumno = User.objects.get(username='alumno1').alumno
        grupo = Grupo.objects.get(id=51)
        evaluacion_original = EvaluacionesDeAlumnos.objects.get(
                              autor=alumno, videoclase=grupo.videoclase)
        valor = 1 if evaluacion_original.valor < 1 else 0
        form_data = {}
        form_data['valor'] = valor
        form_data['videoclase'] = 36
        form = EvaluacionesDeAlumnosForm(form_data)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response
        response = self.client.post(reverse('evaluar_video', kwargs={'pk':27}), form_data)
        self.assertEqual(response.status_code, 200)

        # assert valid edit of object
        evaluacion_editada = EvaluacionesDeAlumnos.objects.get(
                              autor=alumno, videoclase=grupo.videoclase)
        self.assertNotEqual(evaluacion_editada.valor, evaluacion_original.valor)
        self.assertEqual(valor, evaluacion_editada.valor)

    def test_responder_pregunta_correct_data(self):
        self.client.login(username='alumno10', password='alumno')
        alumno = User.objects.get(username='alumno1').alumno
        videoclase = VideoClase.objects.get(id=38)
        form_data = {}
        form_data['videoclase'] = videoclase.id
        form_data['respuesta'] = videoclase.alternativa_correcta
        form = RespuestasDeAlumnosForm(form_data)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response
        response = self.client.get(reverse('evaluar_videoclase', kwargs={'tarea_id':10}), form_data)
        self.assertEqual(response.status_code, 200)

        # assert valid update of object
        obj = form.save(commit=False)
        obj.alumno = alumno
        obj.save()
        respuesta = RespuestasDeAlumnos.objects.filter(videoclase=videoclase, alumno=alumno, 
                                                   respuesta=videoclase.alternativa_correcta).exists()
        self.assertTrue(respuesta)

class ProfesorTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('profesor'))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('profesor'))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('profesor'))
        self.assertEqual(response.status_code, 302)

    def test_profesor_get_cursos_tareas_table(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('profesor'))
        user = User.objects.get(username='profe')
        current_year = timezone.now().year
        tareas = Tarea.objects.filter(curso__profesor=user.profesor) \
                                         .filter(curso__anho=current_year)
        cursos_sin_tarea = Curso.objects.filter(tarea=None)
        self.assertEqual(list(response.context['tareas']), list(tareas))
        self.assertEqual(list(response.context['cursos_sin_tarea']), list(cursos_sin_tarea))

class SubirNotaFormTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('subir_nota'))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('subir_nota'))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('subir_nota'))
        self.assertEqual(response.status_code, 302)

    def test_profesor_subir_nota_form(self):
        self.client.login(username='profe', password='profe')
        alumno_test = Alumno.objects.get(id=5)
        grupo_test = Grupo.objects.filter(alumnos=alumno_test)[0]
        notas_originales = NotasFinales.objects.get(alumno=alumno_test, grupo=grupo_test)
        form_data = {}
        form_data['grupo'] = grupo_test.id
        form_data['alumno'] = alumno_test.id
        form_data['nota'] = 3 if notas_originales.nota_profesor >=4 else 5
        form = SubirNotaForm(form_data)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response
        response = self.client.post(reverse('subir_nota'), form_data)
        self.assertEqual(response.status_code, 200)

        # assert valid edit of object
        notas_editadas = NotasFinales.objects.get(alumno=alumno_test, grupo=grupo_test)
        self.assertNotEqual(notas_editadas.nota_profesor, notas_originales.nota_profesor)
        if notas_originales.nota_profesor >= 4:
            self.assertEqual(notas_editadas.nota_profesor, 3)
        else:
            self.assertEqual(notas_editadas.nota_profesor, 5)

class TareaDetalleTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('tarea', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('tarea', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('tarea', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_tarea_get_data(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('tarea', kwargs={'tarea_id':1}))
        tarea = Tarea.objects.get(id=1)
        user = User.objects.get(username='profe')
        videoclases_recibidas = Grupo.objects.filter(tarea=tarea).exclude(videoclase__video__isnull=True) \
                                .exclude(videoclase__video__exact='').count()
        cursos = user.profesor.cursos.all()
        self.assertEqual(response.context['videoclases_recibidas'], videoclases_recibidas)
        self.assertEqual(response.context['tarea'], tarea)

    def test_editar_tarea_form(self):
        self.client.login(username='profe', password='profe')
        tarea_original = Tarea.objects.get(id=9)
        form_data = {}
        form_data['revisiones'] = 5
        form = EditarTareaForm(form_data)

        # assert valid form
        self.assertTrue(form.is_valid())

        # assert valid response
        response = self.client.post(reverse('editar_tarea_form', kwargs={'tarea_id':9}), form_data)
        self.assertEqual(response.status_code, 200)

        # assert valid edit of object
        tarea_editada = Tarea.objects.get(id=9)
        self.assertNotEqual(tarea_editada.revisiones, tarea_original.revisiones)
        self.assertEqual(5, Tarea.objects.get(id=9).revisiones)

class VerVideoclaseTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_alumno_permissions(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('ver_videoclase', kwargs={'tarea_id':16}))
        self.assertEqual(response.status_code, 200)

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('ver_videoclase', kwargs={'tarea_id':16}))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('ver_videoclase', kwargs={'tarea_id':16}))
        self.assertEqual(response.status_code, 302)

    def test_alumno_tipo_tarea_permissions(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('ver_videoclase', kwargs={'tarea_id':10}))
        self.assertEqual(response.status_code, 302)

    def test_ver_videoclases_get_data(self):
        self.client.login(username='alumno1', password='alumno')
        response = self.client.get(reverse('ver_videoclase', kwargs={'tarea_id':16}))
        alumno = User.objects.get(username='alumno1').alumno
        tarea = Tarea.objects.get(id=16)
        grupo = Grupo.objects.get(tarea=tarea, alumnos=alumno)
        self.assertEqual(response.context['grupo'], grupo)

class VideoClaseModelMethodsTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_porcentaje_me_gusta(self):
        vc = VideoClase.objects.get(id=35)
        me_gusta = EvaluacionesDeAlumnos.objects.filter(videoclase=vc, valor=1).count()
        total = EvaluacionesDeAlumnos.objects.filter(videoclase=vc).count()
        porcentaje = int(round(100*me_gusta/total))
        self.assertEqual(vc.porcentaje_me_gusta(), porcentaje)

    def test_porcentaje_neutro(self):
        vc = VideoClase.objects.get(id=35)
        neutro = EvaluacionesDeAlumnos.objects.filter(videoclase=vc, valor=0).count()
        total = EvaluacionesDeAlumnos.objects.filter(videoclase=vc).count()
        porcentaje = int(round(100*neutro/total))
        self.assertEqual(vc.porcentaje_neutro(), porcentaje)

    def test_porcentaje_no_me_gusta(self):
        vc = VideoClase.objects.get(id=35)
        no_me_gusta = EvaluacionesDeAlumnos.objects.filter(videoclase=vc, valor=-1).count()
        total = EvaluacionesDeAlumnos.objects.filter(videoclase=vc).count()
        porcentaje = int(round(100*no_me_gusta/total))
        self.assertEqual(vc.porcentaje_no_me_gusta(), porcentaje)

    def test_integrantes_porcentaje_me_gusta(self):
        vc = VideoClase.objects.get(id=35)
        otras_vc = VideoClase.objects.filter(grupo__tarea=vc.grupo.tarea) \
                                     .exclude(id=vc.id)
        me_gusta = EvaluacionesDeAlumnos.objects.filter(autor__in=vc.grupo.alumnos.all(), 
                                                        valor=1,
                                                        videoclase__in=otras_vc).count()
        total = EvaluacionesDeAlumnos.objects.filter(autor__in=vc.grupo.alumnos.all(),
                                                     videoclase__in=otras_vc).count()
        porcentaje = int(round(100*me_gusta/total))
        self.assertEqual(vc.integrantes_porcentaje_me_gusta(), porcentaje)

    def test_integrantes_porcentaje_neutro(self):
        vc = VideoClase.objects.get(id=35)
        otras_vc = VideoClase.objects.filter(grupo__tarea=vc.grupo.tarea) \
                                     .exclude(id=vc.id)
        neutro = EvaluacionesDeAlumnos.objects.filter(autor__in=vc.grupo.alumnos.all(), 
                                                      valor=0,
                                                      videoclase__in=otras_vc).count()
        total = EvaluacionesDeAlumnos.objects.filter(autor__in=vc.grupo.alumnos.all(),
                                                     videoclase__in=otras_vc).count()
        porcentaje = int(round(100*neutro/total))
        self.assertEqual(vc.integrantes_porcentaje_neutro(), porcentaje)

    def test_integrantes_porcentaje_no_me_gusta(self):
        vc = VideoClase.objects.get(id=35)
        otras_vc = VideoClase.objects.filter(grupo__tarea=vc.grupo.tarea) \
                                     .exclude(id=vc.id)
        no_me_gusta = EvaluacionesDeAlumnos.objects.filter(autor__in=vc.grupo.alumnos.all(), 
                                                           valor=-1,
                                                           videoclase__in=otras_vc).count()
        total = EvaluacionesDeAlumnos.objects.filter(autor__in=vc.grupo.alumnos.all(),
                                                     videoclase__in=otras_vc).count()
        porcentaje = int(round(100*no_me_gusta/total))
        self.assertEqual(vc.integrantes_porcentaje_no_me_gusta(), porcentaje)

    def test_porcentaje_respuestas_correctas(self):
        vc = VideoClase.objects.get(id=35)
        correctas = RespuestasDeAlumnos.objects \
                    .filter(videoclase=vc, respuesta=vc.alternativa_correcta) \
                    .count()
        total = RespuestasDeAlumnos.objects.filter(videoclase=vc).count()
        porcentaje = int(round(100*correctas/total))
        self.assertEqual(vc.porcentaje_respuestas_correctas(), porcentaje)

    def test_porcentaje_respuestas_incorrectas(self):
        vc = VideoClase.objects.get(id=35)
        incorrectas = RespuestasDeAlumnos.objects \
                      .filter(videoclase=vc, respuesta=vc.alternativa_2) \
                      .count()
        incorrectas += RespuestasDeAlumnos.objects \
                       .filter(videoclase=vc, respuesta=vc.alternativa_3) \
                       .count()
        total = RespuestasDeAlumnos.objects.filter(videoclase=vc).count()
        porcentaje = int(round(100*incorrectas/total))
        self.assertEqual(vc.porcentaje_respuestas_incorrectas(), porcentaje)

    def test_integrantes_y_respuestas(self):
        vc = VideoClase.objects.get(id=35)
        a = vc.grupo.alumnos.all()[0]
        respuestas = RespuestasDeAlumnos.objects.filter(
                        videoclase__grupo__tarea=vc.grupo.tarea,
                        alumno=a)
        correctas = 0
        for r in respuestas:
            correctas += r.respuesta == r.videoclase.alternativa_correcta
        incorrectas = 0
        for r in respuestas:
            incorrectas += r.respuesta == r.videoclase.alternativa_2 \
                or r.respuesta == r.videoclase.alternativa_3
        result_dict = vc.integrantes_y_respuestas()
        self.assertEqual(result_dict[0]['cantidad_correctas'], correctas)
        self.assertEqual(result_dict[0]['cantidad_incorrectas'], incorrectas)

class VideoclasesAlumnoTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('videoclases_alumno', kwargs={'alumno_id':1}))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('videoclases_alumno', kwargs={'alumno_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('videoclases_alumno', kwargs={'alumno_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_videoclases_alumno_get_data(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('videoclases_alumno', kwargs={'alumno_id':1}))
        alumno = Alumno.objects.get(id=1)
        grupos = alumno.grupo_set.exclude(videoclase__video=None).exclude(videoclase__video__exact='')
        grupos_pendientes = alumno.grupo_set.filter(Q(videoclase__video='') | Q(videoclase__video__isnull=True))
        vmerge = grupos | grupos_pendientes
        vmerge.order_by('-id')
        self.assertEqual(response.context['alumno'], alumno)
        self.assertEqual(list(response.context['grupos']), list(vmerge))

class VideoclasesTareaTestCase(TestCase):
    fixtures = todos_los_fixtures

    def test_profesor_permissions(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('videoclases_tarea', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 200)

    def test_alumno_permissions(self):
        self.client.login(username='alumno', password='alumno')
        response = self.client.get(reverse('videoclases_tarea', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_permissions(self):
        response = self.client.get(reverse('videoclases_tarea', kwargs={'tarea_id':1}))
        self.assertEqual(response.status_code, 302)

    def test_videoclases_tarea_get_data(self):
        self.client.login(username='profe', password='profe')
        response = self.client.get(reverse('videoclases_tarea', kwargs={'tarea_id':1}))
        tarea = Tarea.objects.get(id=1)
        self.assertEqual(response.context['tarea'], tarea)
        self.assertEqual(list(response.context['grupos']), list(tarea.grupos.all()))