from django.db import models
import datetime

from videoclases.models.school import School


class Course(models.Model):
    school = models.ForeignKey(School)
    name = models.CharField(max_length=256)
    year = models.IntegerField(default=datetime.datetime.now().year)

    def __str__(self):
        return self.name + ' ' + str(self.year)