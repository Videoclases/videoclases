import urlparse

from django.db import models
from django.db.models import Q

from videoclases.models.grupo import Grupo


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
        from videoclases.models.evaluaciones_de_alumnos import EvaluacionesDeAlumnos
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
        from videoclases.models.evaluaciones_de_alumnos import EvaluacionesDeAlumnos
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
        from videoclases.models.respuestas_de_alumnos import RespuestasDeAlumnos
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
        from videoclases.models.respuestas_de_alumnos import RespuestasDeAlumnos
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
        return 'Curso: ' + self.grupo.tarea.curso.nombre + '. Tarea: ' + \
        self.grupo.tarea.titulo + '. Grupo: ' + str(self.grupo.numero)