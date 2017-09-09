from django.db import models

from videoclases.models.student import Student
from videoclases.models.homework import Homework


class GroupOfStudents(models.Model):
    number         = models.IntegerField()
    homework          = models.ForeignKey(Homework, related_name='groups')
    students        = models.ManyToManyField(Student)

    class Meta:
        unique_together = (('number', 'homework'),)

    def __str__(self):
        return 'Course: ' + self.homework.course.name + '. Homework: ' + \
        self.homework.title + '. GroupOfStudents: ' + str(self.number)