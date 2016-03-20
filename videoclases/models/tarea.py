import urlparse

from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils import timezone

from videoclases.models.curso import Curso
from videoclases.models.profesor import Profesor


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

    def get_uploaded_videoclases(self):
        count = 0
        for g in self.grupos.all():
            if g.videoclase.video not in [None, '']:
                count += 1
        return count

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