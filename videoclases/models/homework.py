# coding=utf-8
from urllib.parse import urlparse,parse_qs
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils import timezone

from videoclases.models.course import Course

from videoclases.models.evaluation.criterias_by_teacher import CriteriasByTeacher
from videoclases.models.evaluation.scala import Scala
from videoclases.models.teacher import Teacher


class Homework(models.Model):
    states = (
        (u'Pendiente', 1),
        (u'Evaluando', 2),
        (u'Terminada', 3),
    )

    teacher = models.ForeignKey(Teacher)
    course = models.ForeignKey(Course, related_name='course_homework')
    title = models.CharField(max_length=80)
    description = models.TextField(validators=[MaxLengthValidator(400)])
    video = models.CharField(max_length=100, blank=True, null=True)
    date_upload = models.DateField()
    date_evaluation = models.DateField()
    revision = models.IntegerField(default=3)
    homework_to_evaluate = models.ForeignKey('Homework', blank=True, null=True)
    criterias = models.ManyToManyField(CriteriasByTeacher, blank=True)
    scala = models.ForeignKey(Scala, null=True, blank=True)

    def __str__(self):
        return u"Curso: {0}, {1}".format(self.course.name,self.title)

    def full_name(self):
        return u"Curso: {0} {1}, {2}".format(
            self.course.name,
            self.course.year,
            self.title)

    def get_estado(self):
        today = timezone.datetime.date(timezone.datetime.today())
        dictionary = dict(self.states)
        if today <= self.date_upload:
            return dictionary.get('Pendiente')
        elif today <= self.date_evaluation:
            return dictionary.get('Evaluando')
        else:
            return dictionary.get('Terminada')

    def get_estado_nombre(self):
        today = timezone.datetime.date(timezone.datetime.today())
        dictionary = dict(self.states)
        if today <= self.date_upload:
            return 'Pendiente'
        elif today <= self.date_evaluation:
            return 'Evaluando'
        else:
            return 'Terminada'

    def get_uploaded_videoclases(self):
        count = 0
        for g in self.groups.all():
            if g.videoclase.video not in [None, '']:
                count += 1
        return count

    @staticmethod
    def process_youtube_default_link(link):
        if 'youtu.be/' in link:
            video_id = link.split('youtu.be/',1)[1]
            return 'https://www.youtube.com/embed/' + str(video_id), True
        url_data = urlparse(link)
        query = parse_qs(url_data.query)
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
                self.video = str(link)
        super(Homework, self).save(*args, **kwargs)