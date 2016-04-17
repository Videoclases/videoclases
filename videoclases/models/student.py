from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from videoclases.models.course import Course


class Student(models.Model):
    user = models.OneToOneField(User)
    courses = models.ManyToManyField(Course, related_name='students')
    changed_password = models.BooleanField(default=False)

    def course_actual(self):
        course_qs = self.courses.filter(year=timezone.now().year)
        return course_qs[0] if course_qs.exists() else False

    def __unicode__(self):
        if self.course_actual():
            return 'Course: ' + self.course_actual().name + ' ' + str(self.course_actual().year) + ' ' + \
                   self.user.get_full_name()
        return 'Sin courses actualmente'