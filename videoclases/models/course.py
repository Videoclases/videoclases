from django.db import models

from videoclases.models.school import School


class Course(models.Model):
    school = models.ForeignKey(School)
    name = models.CharField(max_length=256)
    year = models.IntegerField(default=2015)

    def __unicode__(self):
        return self.name + ' ' + str(self.year)