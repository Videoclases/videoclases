from django.contrib import admin
from django.conf.urls import url

import quality_control.views.control_views as cv

admin.autodiscover()


urlpatterns = [
    url(r'^new/$', cv.NewControlView.as_view(), name='new_control'),
]