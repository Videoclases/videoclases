from django.db import models

from videoclases.models.student import Student
from videoclases.models.video_clase import VideoClase


class StudentResponses(models.Model):
    videoclase = models.ForeignKey(VideoClase, related_name='answers')
    student = models.ForeignKey(Student)
    answer = models.CharField(max_length=100, blank=True, null=True)

    def is_correct(self):
        return self.answer == self.videoclase.correct_alternative

    def __str__(self):
        return 'Responde: ' + self.student.user.first_name + '. Respuesta: ' + str(self.answer) + \
        ' .Videoclase ' + str(self.videoclase.id) + ' ' + self.videoclase.homework.title
