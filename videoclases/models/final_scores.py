from django.db import models

from videoclases.models.student import Student
from videoclases.models.groupofstudents import GroupOfStudents


class FinalScores(models.Model):
    group = models.ForeignKey(GroupOfStudents)
    student = models.ForeignKey(Student)
    class_score = models.FloatField(default=0, blank=True, null=True)
    teacher_score = models.FloatField(default=0)

    def ponderar_notas(self):
        return self.teacher_score

    def __str__(self):
        return 'Curso: ' + self.group.homework.course.name + '. Tarea: ' + \
        self.group.homework.title + '. Grupo: ' + str(self.group.number) + \
        '. Nota: ' + str(self.ponderar_notas())