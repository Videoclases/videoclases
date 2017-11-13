from django.conf.urls import url
from django.contrib import admin

import quality_control.views.api as api
import quality_control.views.control_views as cv

admin.autodiscover()


urlpatterns = [
    url(r'^new/$', cv.NewControlView.as_view(), name='new_control'),
    url(r'^homework/(?P<pk>\d+)/evaluate/$', api.GetVideoClaseView.as_view(), name='api_get_videoclase'),
    url(r'^homework/(?P<pk>\d+)/evaluate-teacher/$', api.GetVideoClaseTeacherView.as_view(),
        name='api_get_videoclase_teacher'),
    url(r'^homework/(?P<homework_id>\d+)/evaluations/$',
        api.descargar_homework_evaluation,
        name='descargar_homework_evaluations'),
]