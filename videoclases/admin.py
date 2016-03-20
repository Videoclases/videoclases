from django.contrib import admin

from videoclases.models.alumno import Alumno
from videoclases.models.boolean_parameters import BooleanParameters
from videoclases.models.colegio import Colegio
from videoclases.models.curso import Curso
from videoclases.models.evaluaciones_de_alumnos import EvaluacionesDeAlumnos
from videoclases.models.grupo import Grupo
from videoclases.models.notas_finales import NotasFinales
from videoclases.models.profesor import Profesor
from videoclases.models.respuestas_de_alumnos import RespuestasDeAlumnos
from videoclases.models.tarea import Tarea
from videoclases.models.video_clase import VideoClase

admin.site.register(Alumno)
admin.site.register(BooleanParameters)
admin.site.register(Colegio)
admin.site.register(Curso)
admin.site.register(EvaluacionesDeAlumnos)
admin.site.register(Grupo)
admin.site.register(NotasFinales)
admin.site.register(Profesor)
admin.site.register(RespuestasDeAlumnos)
admin.site.register(Tarea)
admin.site.register(VideoClase)
