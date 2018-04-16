from django.contrib.auth.models import User
from django.db import models

from videoclases.models.school import School
from videoclases.models.course import Course


class Teacher(models.Model):
    school = models.ForeignKey(School)
    user = models.OneToOneField(User)
    courses = models.ManyToManyField(Course, blank=True)
    changed_password = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name