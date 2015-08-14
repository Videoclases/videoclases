from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import videoclases.views as vv

urlpatterns = patterns('',
    url(r'^$', vv.IndexView.as_view(), name='index'),
    url(r'^alumno/enviar-videoclase/(?P<tarea_id>\d+)/$', vv.EnviarVideoclaseView.as_view(), name='enviar_videoclase'),
    url(r'^alumno/evaluar-video/(?P<pk>\d+)/$', vv.EvaluacionesDeAlumnosFormView.as_view(), name='evaluar_video'),
    url(r'^alumno/evaluar-videoclase/(?P<tarea_id>\d+)/$', vv.EvaluarVideoclaseView.as_view(), name='evaluar_videoclase'),
    url(r'^alumno/ver-videoclase/(?P<tarea_id>\d+)/$', vv.VerVideoclaseView.as_view(), name='ver_videoclase'),
    url(r'^alumno/', vv.AlumnoView.as_view(), name='alumno'),
    url(r'^login/', vv.IndexView.as_view(), name='login'),
    url(r'^logout/', vv.logout_view, name='logout'),
    url(r'^profesor/alumnos/(?P<alumno_id>\d+)/$', vv.VideoclasesAlumnoView.as_view(), name='videoclases_alumno'),
    url(r'^profesor/asignar-grupo-form/', vv.AsignarGrupoFormView.as_view(), name='asignar_grupo_form'),
    url(r'^profesor/crear-curso/', vv.CrearCursoFormView.as_view(), name='crear_curso'),
    url(r'^profesor/crear-tarea/', vv.CrearTareaView.as_view(), name='crear_tarea'),
    url(r'^profesor/crear-tarea-form/', vv.CrearTareaFormView.as_view(), name='crear_tarea_form'),
    url(r'^profesor/curso/(?P<curso_id>\d+)/$', vv.CursoView.as_view(), name='curso'),
    url(r'^profesor/descargar-curso/(?P<curso_id>\d+)/$', vv.descargar_curso, name='descargar_curso'),
    url(r'^profesor/descargar-grupos-tarea/(?P<tarea_id>\d+)/$', vv.descargar_grupos_tarea, name='descargar_grupos_tarea'),
    url(r'^profesor/editar-tarea-form/(?P<tarea_id>\d+)/$', vv.TareaDetalleView.as_view(), name='editar_tarea_form'),
    url(r'^profesor/subir-nota/', vv.SubirNotaFormView.as_view(), name='subir_nota'),
    url(r'^profesor/tarea/(?P<tarea_id>\d+)/$', vv.TareaDetalleView.as_view(), name='tarea'),
    url(r'^profesor/videoclases-tarea/(?P<tarea_id>\d+)/', vv.VideoclasesTareaView.as_view(), name='videoclases_tarea'),
    url(r'^profesor/', vv.ProfesorView.as_view(), name='profesor'),
    #url(r'^videoclases/', vv.videoclases, name='videoclases'),

    url(r'^admin/', include(admin.site.urls)),
)
