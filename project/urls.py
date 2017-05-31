from django.conf.urls import patterns, include, url

from django.contrib import admin
from quality_control.admin import admin_site
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^admin2/', include(admin_site.urls)),
                       url(r'^', include('videoclases.urls')),
                       url(r'^quality/', include('quality_control.urls')),
                       )
