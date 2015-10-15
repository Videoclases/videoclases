#-*- coding: UTF-8 -*-

import urlparse
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.utils import timezone

class BooleanParameters(models.Model):
    description = models.CharField(max_length=256)
    value = models.BooleanField()

    def __unicode__(self):
        return self.description + ': ' + str(self.value)

    class Meta:
        verbose_name = 'Mis Parámetros'
        verbose_name_plural = 'Mis Parámetros'

class Colegio(models.Model):
    nombre = models.CharField(max_length=64)

    def __unicode__(self):
        return self.nombre

class Curso(models.Model):
    colegio = models.ForeignKey(Colegio)
    nombre = models.CharField(max_length=256)
    anho = models.IntegerField(default=2015)

    def __unicode__(self):
        return self.nombre + ' ' + str(self.anho)

class Profesor(models.Model):
    colegio = models.ForeignKey(Colegio)
    usuario = models.OneToOneField(User)
    cursos = models.ManyToManyField(Curso, blank=True)
    changed_password = models.BooleanField(default=False)

    def __unicode__(self):
        return self.usuario.first_name + ' ' + self.usuario.last_name

class Alumno(models.Model):
    usuario = models.OneToOneField(User)
    cursos = models.ManyToManyField(Curso, related_name='alumnos')
    changed_password = models.BooleanField(default=False)

    def curso_actual(self):
        curso_qs = self.cursos.filter(anho=timezone.now().year)
        return curso_qs[0] if curso_qs.exists() else False

    def __unicode__(self):
        return 'Curso: ' + self.curso_actual().nombre + ' ' + str(self.curso_actual().anho) + ' ' + \
        self.usuario.get_full_name()

class Tarea(models.Model):
    estados = (
        (u'Pendiente', 1),
        (u'Evaluando', 2),
        (u'Terminada', 3),
    )

    profesor = models.ForeignKey(Profesor)
    curso = models.ForeignKey(Curso)
    titulo = models.CharField(max_length=80)
    descripcion = models.TextField(validators=[MaxLengthValidator(400)])
    video = models.CharField(max_length=100, blank=True, null=True)
    fecha_subida = models.DateField()
    fecha_evaluacion = models.DateField()
    revisiones = models.IntegerField(default=3)

    def __unicode__(self):
        return 'Curso: ' + self.curso.nombre + ' ' + str(self.curso.anho) + ' ' + \
        self.titulo

    def get_estado(self):
        today = timezone.datetime.date(timezone.datetime.today())
        dictionary = dict(self.estados)
        if today <= self.fecha_subida:
            return dictionary.get('Pendiente')
        elif today <= self.fecha_evaluacion:
            return dictionary.get('Evaluando')
        else:
            return dictionary.get('Terminada')

    def get_estado_nombre(self):
        today = timezone.datetime.date(timezone.datetime.today())
        dictionary = dict(self.estados)
        if today <= self.fecha_subida:
            return 'Pendiente'
        elif today <= self.fecha_evaluacion:
            return 'Evaluando'
        else:
            return 'Terminada'

    @staticmethod
    def process_youtube_default_link(link):
        if 'youtu.be/' in link:
            video_id = link.split('youtu.be/',1)[1]
            return 'https://www.youtube.com/embed/' + str(video_id), True
        url_data = urlparse.urlparse(link)
        query = urlparse.parse_qs(url_data.query)
        if 'youtube.com/embed/' in link:
            return link, True
        try:
            video_id = query['v'][0]
            return 'https://www.youtube.com/embed/' + str(video_id), True
        except:
            return None, False

    def save(self, *args, **kwargs):
        if self.video:
            link, success = self.process_youtube_default_link(self.video)
            if success:
                self.video = unicode(link)
        super(Tarea, self).save(*args, **kwargs)

class Grupo(models.Model):
    numero         = models.IntegerField()
    tarea          = models.ForeignKey(Tarea, related_name='grupos')
    alumnos        = models.ManyToManyField(Alumno)

    class Meta:
        unique_together = (('numero', 'tarea'),)

    def __unicode__(self):
        return 'Tarea: ' + self.tarea.titulo + '. Grupo: ' + str(self.numero)

class VideoClase(models.Model):
    grupo          = models.OneToOneField(Grupo)
    video          = models.CharField(max_length=100, blank=True, null=True)
    pregunta       = models.CharField(max_length=100, blank=True, null=True)
    alternativa_correcta = models.CharField(max_length=100, blank=True, null=True)
    alternativa_2  = models.CharField(max_length=100, blank=True, null=True)
    alternativa_3  = models.CharField(max_length=100, blank=True, null=True)
    alumnos_subida = models.DateTimeField(blank=True, null=True)

    # EvaluacionesDeAlumnos
    def calcular_porcentaje_evaluaciones(self, valor):
        conjunto = self.evaluaciones.filter(videoclase=self, valor=valor).count()
        total = self.evaluaciones.filter(videoclase=self).count()
        return int(round(100*conjunto/total)) if total else 0

    def porcentaje_me_gusta(self):
        return self.calcular_porcentaje_evaluaciones(1)

    def porcentaje_neutro(self):
        return self.calcular_porcentaje_evaluaciones(0)

    def porcentaje_no_me_gusta(self):
        return self.calcular_porcentaje_evaluaciones(-1)

    def cantidad_me_gusta(self):
        return self.evaluaciones.filter(videoclase=self, valor=1).count()

    def cantidad_neutro(self):
        return self.evaluaciones.filter(videoclase=self, valor=0).count()

    def cantidad_no_me_gusta(self):
        return self.evaluaciones.filter(videoclase=self, valor=-1).count()

    def integrantes_calcular_porcentaje_evaluaciones(self, valor):
        otras_vc = VideoClase.objects.filter(grupo__tarea=self.grupo.tarea) \
                                     .exclude(id=self.id)
        conjunto = EvaluacionesDeAlumnos.objects.filter(autor__in=self.grupo.alumnos.all(), 
                                                        valor=valor,
                                                        videoclase__in=otras_vc).count()
        total = EvaluacionesDeAlumnos.objects.filter(autor__in=self.grupo.alumnos.all(),
                                                     videoclase__in=otras_vc).count()
        return int(round(100*conjunto/total)) if total else 0

    def integrantes_porcentaje_me_gusta(self):
        return self.integrantes_calcular_porcentaje_evaluaciones(1)

    def integrantes_porcentaje_neutro(self):
        return self.integrantes_calcular_porcentaje_evaluaciones(0)

    def integrantes_porcentaje_no_me_gusta(self):
        return self.integrantes_calcular_porcentaje_evaluaciones(-1)

    def calcular_integrantes_cantidad_votos(self, valor):
        otras_vc = VideoClase.objects.filter(grupo__tarea=self.grupo.tarea) \
                                     .exclude(id=self.id)
        return EvaluacionesDeAlumnos.objects.filter(autor__in=self.grupo.alumnos.all(),
                                                    valor=valor,
                                                    videoclase__in=otras_vc).count()

    def integrantes_cantidad_me_gusta(self):
        return self.calcular_integrantes_cantidad_votos(1)

    def integrantes_cantidad_neutro(self):
        return self.calcular_integrantes_cantidad_votos(0)

    def integrantes_cantidad_no_me_gusta(self):
        return self.calcular_integrantes_cantidad_votos(-1)

    # RespuestasDeAlumnos
    def calcular_porcentaje_respuestas(self, respuestas):
        conjunto = 0
        for r in respuestas:
            conjunto += self.respuestas.filter(videoclase=self, respuesta=r).count()
        total = self.respuestas.filter(videoclase=self).count()
        return int(round(100*conjunto/total)) if total else 0

    def porcentaje_respuestas_correctas(self):
        return self.calcular_porcentaje_respuestas([self.alternativa_correcta])

    def porcentaje_respuestas_incorrectas(self):
        return self.calcular_porcentaje_respuestas([self.alternativa_2, self.alternativa_3])

    def cantidad_correctas(self):
        return self.respuestas.filter(videoclase=self, respuesta=self.alternativa_correcta).count()

    def cantidad_incorrectas(self):
        return self.respuestas.filter(videoclase=self, respuesta__in=[self.alternativa_2, 
                                                                      self.alternativa_3]).count()

    def integrantes_y_respuestas(self):
        alumnos = self.grupo.alumnos.all()
        alumnos_array = []
        for a in alumnos:
            alumno_dict = {}
            respuestas = RespuestasDeAlumnos.objects.filter(
                            videoclase__grupo__tarea=self.grupo.tarea,
                            alumno=a)
            correctas = 0
            for r in respuestas:
                correctas += r.respuesta == r.videoclase.alternativa_correcta
            incorrectas = 0
            for r in respuestas:
                incorrectas += r.respuesta == r.videoclase.alternativa_2 \
                    or r.respuesta == r.videoclase.alternativa_3
            alumno_dict['user_id'] = a.usuario.id
            alumno_dict['nombre'] = a.usuario.first_name + ' ' + a.usuario.last_name
            alumno_dict['cantidad_correctas'] = correctas
            alumno_dict['cantidad_incorrectas'] = incorrectas
            total = correctas + incorrectas
            alumno_dict['porcentaje_correctas'] = int(round(100*correctas/total)) if total else 0
            alumno_dict['porcentaje_incorrectas'] = int(round(100*incorrectas/total)) if total else 0
            alumnos_array.append(alumno_dict)
        return alumnos_array

    def respuestas_de_otros(self):
        correctas = RespuestasDeAlumnos.objects.filter(
                        videoclase=self, 
                        respuesta=self.alternativa_correcta).count()
        incorrectas = RespuestasDeAlumnos.objects.filter(
                            videoclase=self) \
                            .filter(Q(respuesta=self.alternativa_2) | Q(respuesta=self.alternativa_3)) \
                            .count()
        return_dict = {}
        return_dict['correctas'] = correctas
        return_dict['incorrectas'] = incorrectas
        return return_dict

    @staticmethod
    def process_youtube_default_link(link):
        if 'youtu.be/' in link:
            video_id = link.split('youtu.be/',1)[1]
            return 'https://www.youtube.com/embed/' + str(video_id), True
        url_data = urlparse.urlparse(link)
        query = urlparse.parse_qs(url_data.query)
        try:
            video_id = query['v'][0]
            return 'https://www.youtube.com/embed/' + str(video_id), True
        except:
            return None, False

    def save(self, *args, **kwargs):
        if self.video:
            link, success = self.process_youtube_default_link(self.video)
            if success:
                self.video = link
        super(VideoClase, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Tarea: ' + self.grupo.tarea.titulo + '. Grupo: ' + str(self.grupo.numero)

class NotasFinales(models.Model):
    grupo = models.ForeignKey(Grupo)
    alumno = models.ForeignKey(Alumno)
    nota_clase = models.FloatField(default=0, blank=True, null=True)
    nota_profesor = models.FloatField(default=0)

    def ponderar_notas(self):
        return self.nota_profesor

    def __unicode__(self):
        return 'Tarea: ' + self.grupo.tarea.titulo + '. Grupo: ' + str(self.grupo.numero) + \
        '. Nota: ' + str(self.ponderar_notas())

class EvaluacionesDeAlumnos(models.Model):
    evaluaciones = (
        (u'No me gusta', -1),
        (u'Neutro', 0),
        (u'Me gusta', 1),
    )

    autor = models.ForeignKey(Alumno)
    valor = models.IntegerField(default=0)
    videoclase = models.ForeignKey(VideoClase, related_name='evaluaciones')

    def __unicode__(self):
        return 'Autor: ' + self.autor.usuario.first_name + '. Valor: ' + str(self.valor)

class RespuestasDeAlumnos(models.Model):
    videoclase = models.ForeignKey(VideoClase, related_name='respuestas')
    alumno = models.ForeignKey(Alumno)
    respuesta = models.CharField(max_length=100, blank=True, null=True)

    def is_correct(self):
        return self.respuesta == self.videoclase.alternativa_correcta

    def __unicode__(self):
        return 'Responde: ' + self.alumno.usuario.first_name + '. Respuesta: ' + unicode(self.respuesta) + \
        ' .Videoclase ' + str(self.videoclase.id) + ' ' + self.videoclase.grupo.tarea.titulo