from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from quality_control.admin import admin_site
admin.autodiscover()

urlpatterns = [
                   url(r'^admin/', include(admin.site.urls)),
                   url(r'^admin2/', include(admin_site.urls)),
                   url(r'^', include('videoclases.urls')),
                   url(r'^api/', include('quality_control.urls')),
            ]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
