import urlparse

from django.db import models
from django.db.models import Q

from videoclases.models.groupofstudents import GroupOfStudents


class VideoClase(models.Model):
    group          = models.OneToOneField(GroupOfStudents)
    video          = models.CharField(max_length=100, blank=True, null=True)
    question       = models.CharField(max_length=100, blank=True, null=True)
    correct_alternative = models.CharField(max_length=100, blank=True, null=True)
    alternative_2  = models.CharField(max_length=100, blank=True, null=True)
    alternative_3  = models.CharField(max_length=100, blank=True, null=True)
    upload_students = models.DateTimeField(blank=True, null=True)

    # StudentEvaluations
    def calcular_porcentaje_evaluaciones(self, value):
        conjunto = self.evaluations.filter(videoclase=self, value=value).count()
        total = self.evaluations.filter(videoclase=self).count()
        return int(round(100*conjunto/total)) if total else 0

    def porcentaje_me_gusta(self):
        return self.calcular_porcentaje_evaluaciones(1)

    def porcentaje_neutro(self):
        return self.calcular_porcentaje_evaluaciones(0)

    def porcentaje_no_me_gusta(self):
        return self.calcular_porcentaje_evaluaciones(-1)

    def cantidad_me_gusta(self):
        return self.evaluations.filter(videoclase=self, value=1).count()

    def cantidad_neutro(self):
        return self.evaluations.filter(videoclase=self, value=0).count()

    def cantidad_no_me_gusta(self):
        return self.evaluations.filter(videoclase=self, value=-1).count()

    def integrantes_calcular_porcentaje_evaluaciones(self, value):
        from videoclases.models.student_evaluations import StudentEvaluations
        otras_vc = VideoClase.objects.filter(group__homework=self.group.homework) \
                                     .exclude(id=self.id)
        conjunto = StudentEvaluations.objects.filter(author__in=self.group.students.all(),
                                                     value=value,
                                                     videoclase__in=otras_vc).count()
        total = StudentEvaluations.objects.filter(author__in=self.group.students.all(),
                                                  videoclase__in=otras_vc).count()
        return int(round(100*conjunto/total)) if total else 0

    def integrantes_porcentaje_me_gusta(self):
        return self.integrantes_calcular_porcentaje_evaluaciones(1)

    def integrantes_porcentaje_neutro(self):
        return self.integrantes_calcular_porcentaje_evaluaciones(0)

    def integrantes_porcentaje_no_me_gusta(self):
        return self.integrantes_calcular_porcentaje_evaluaciones(-1)

    def calcular_integrantes_cantidad_votos(self, value):
        from videoclases.models.student_evaluations import StudentEvaluations
        otras_vc = VideoClase.objects.filter(group__homework=self.group.homework) \
                                     .exclude(id=self.id)
        return StudentEvaluations.objects.filter(author__in=self.group.students.all(),
                                                 value=value,
                                                 videoclase__in=otras_vc).count()

    def integrantes_cantidad_me_gusta(self):
        return self.calcular_integrantes_cantidad_votos(1)

    def integrantes_cantidad_neutro(self):
        return self.calcular_integrantes_cantidad_votos(0)

    def integrantes_cantidad_no_me_gusta(self):
        return self.calcular_integrantes_cantidad_votos(-1)

    # StudentResponses
    def calcular_porcentaje_answers(self, answers):
        conjunto = 0
        for r in answers:
            conjunto += self.answers.filter(videoclase=self, answer=r).count()
        total = self.answers.filter(videoclase=self).count()
        return int(round(100*conjunto/total)) if total else 0

    def porcentaje_answers_correctas(self):
        return self.calcular_porcentaje_answers([self.correct_alternative])

    def porcentaje_answers_incorrectas(self):
        return self.calcular_porcentaje_answers([self.alternative_2, self.alternative_3])

    def cantidad_correctas(self):
        return self.answers.filter(videoclase=self, answer=self.correct_alternative).count()

    def cantidad_incorrectas(self):
        answer = self.answers.filter(videoclase=self)
        return answer.count() - answer.filter(answer=self.correct_alternative).count()

    def integrantes_y_answers(self):
        from videoclases.models.student_responses import StudentResponses
        students = self.group.students.all()
        students_array = []
        for a in students:
            student_dict = {}
            homework = self.group.homework
            if homework.homework_to_evaluate is not None:
                homework = homework.homework_to_evaluate
            answers = StudentResponses.objects.filter(
                            videoclase__group__homework=homework,
                            student=a)
            correctas = 0
            for r in answers:
                correctas += r.answer == r.videoclase.correct_alternative
            incorrectas = 0
            for r in answers:
                incorrectas += r.answer == r.videoclase.alternative_2 \
                    or r.answer == r.videoclase.alternative_3
            student_dict['user_id'] = a.user.id
            student_dict['name'] = a.user.first_name + ' ' + a.user.last_name
            student_dict['cantidad_correctas'] = correctas
            student_dict['cantidad_incorrectas'] = incorrectas
            total = correctas + incorrectas
            student_dict['porcentaje_correctas'] = int(round(100*correctas/total)) if total else 0
            student_dict['porcentaje_incorrectas'] = int(round(100*incorrectas/total)) if total else 0
            students_array.append(student_dict)
        return students_array

    def answers_de_otros(self):
        from videoclases.models.student_responses import StudentResponses
        correctas = StudentResponses.objects.filter(
                        videoclase=self,
                        answer=self.correct_alternative).count()
        incorrectas = StudentResponses.objects.filter(
                            videoclase=self) \
                            .filter(Q(answer=self.alternative_2) | Q(answer=self.alternative_3)) \
                            .count()
        return_dict = {}
        return_dict['correctas'] = correctas
        return_dict['incorrectas'] = incorrectas
        return return_dict

    def get_multiple_criteria_score(self):
        from videoclases.models.student_evaluations import StudentEvaluations
        from django.db.models import Avg
        evaluations = StudentEvaluations.objects.filter(videoclase=self)
        result = evaluations.aggregate(format=Avg('format'),
                                     copyright=Avg('copyright'),
                                     theme=Avg('theme'),
                                     pedagogical=Avg('pedagogical'),
                                     rythm=Avg('rythm'),
                                     originality=Avg('originality')
                                     )
        try:
            result['total'] = sum(result.values()) + 1
        except TypeError:
            result['total'] = ''
        return result

    @staticmethod
    def process_youtube_default_link(link):
        if 'youtu.be/' in link:
            video_id = link.split('youtu.be/',1)[1]
            return 'https://www.youtube.com/embed/' + str(video_id), True
        url_data = urlparse.urlparse(link)
        query = urlparse.parse_qs(url_data.query)
        try:
            video_id = query['v'][0]
            return 'https://www.youtube.com/embed/' + str(video_id), True
        except:
            return None, False

    def save(self, *args, **kwargs):
        if self.video:
            link, success = self.process_youtube_default_link(self.video)
            if success:
                self.video = link
        super(VideoClase, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Curso: ' + self.group.homework.course.name + '. Tarea: ' + \
        self.group.homework.title + '. Grupo de Estudiantes: ' + str(self.group.number)
