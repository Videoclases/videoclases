# coding=utf-8
from django.contrib import admin

from videoclases.models.evaluation.criteria import Criteria
from videoclases.models.evaluation.criterias_by_teacher import CriteriasByTeacher
from videoclases.models.evaluation.scala import Scala
from videoclases.models.evaluation.scala_value import ScalaValue
from videoclases.models.pedagogical_questions.alternative import Alternative
from videoclases.models.pedagogical_questions.pedagogical_questions import PedagogicalQuestions
from videoclases.models.pedagogical_questions.pedagogical_questions_answers import PedagogicalQuestionsAnswers
from videoclases.models.pedagogical_questions.question import Question
from videoclases.models.pedagogical_questions.response import Response
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


class VideoClaseAdmin(admin.ModelAdmin):
    readonly_fields = ('group',)
    list_per_page = 20

class StudentEvaluationsAdmin(admin.ModelAdmin):
    readonly_fields = ('videoclase', 'author')
    list_per_page = 20


admin.site.register(Student)
admin.site.register(BooleanParameters)
admin.site.register(School)
admin.site.register(Course)
admin.site.register(StudentEvaluations,StudentEvaluationsAdmin)
admin.site.register(GroupOfStudents)
admin.site.register(FinalScores)
admin.site.register(Teacher)
admin.site.register(StudentResponses)
admin.site.register(Homework)
admin.site.register(VideoClase, VideoClaseAdmin)
admin.site.register(PedagogicalQuestions)
admin.site.register(PedagogicalQuestionsAnswers)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(Alternative)

admin.site.register(CriteriasByTeacher)
admin.site.register(Criteria)
admin.site.register(Scala)
admin.site.register(ScalaValue)
