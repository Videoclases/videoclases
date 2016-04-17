from django.contrib import admin

from videoclases.models.student import Student
from videoclases.models.boolean_parameters import BooleanParameters
from videoclases.models.school import School
from videoclases.models.course import Course
from videoclases.models.student_evaluations import StudentEvaluations
from videoclases.models.groupofstudents import GroupOfStudents
from videoclases.models.final_scores import FinalScores
from videoclases.models.teacher import Teacher
from videoclases.models.student_responses import StudentResponses
from videoclases.models.homework import Homework
from videoclases.models.video_clase import VideoClase

admin.site.register(Student)
admin.site.register(BooleanParameters)
admin.site.register(School)
admin.site.register(Course)
admin.site.register(StudentEvaluations)
admin.site.register(GroupOfStudents)
admin.site.register(FinalScores)
admin.site.register(Teacher)
admin.site.register(StudentResponses)
admin.site.register(Homework)
admin.site.register(VideoClase)
