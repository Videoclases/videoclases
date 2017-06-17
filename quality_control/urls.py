from django.contrib import admin
from django.conf.urls import url

import quality_control.views.control_views as cv
import quality_control.views.api as api

admin.autodiscover()


urlpatterns = [
    url(r'^new/$', cv.NewControlView.as_view(), name='new_control'),
    url(r'^homework/(?P<pk>\d+)/evaluate/$', api.GetVideoClaseView.as_view(), name='api_get_videoclase'),
]