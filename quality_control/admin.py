from django.contrib.admin import AdminSite

from django.contrib import admin

from quality_control.models.quality_control import QualityControl
from quality_control.models.quality_item import QualityItem
from quality_control.models.quality_score import QualityScore
from videoclases.models.course import Course
from videoclases.models.homework import Homework
from videoclases.models.video_clase import VideoClase


class MyAdminSite(AdminSite):
    site_header = 'Vista custom'

    def has_permission(self, request):
        # Don't care if the user is staff
        return request.user.is_active
admin_site = MyAdminSite(name='mynotadminsite')

class CustomModelAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True


def teacher_courses(request):
    try:
        import datetime
        year = datetime.date.today().year
        courses = request.user.teacher.courses.filter(year=year)
        return courses
    except Exception:
        return []


class QualityModelAdmin(CustomModelAdmin):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "homework":
            kwargs["queryset"] = Homework.objects.filter(course__in=teacher_courses(request))
        return super(QualityModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def queryset(self, request):
        """Limit Pages to those that belong to the request's user."""
        qs = super(QualityModelAdmin, self).queryset(request)
        if request.user.is_superuser:
            # It is mine, all mine. Just return everything.
            return qs.filter(homework__course__in=teacher_courses(request))
        # Now we just add an extra filter on the queryset and
        # we're done. Assumption: Page.owner is a foreignkey
        # to a User.
        return qs.filter(homework__course__in=teacher_courses(request))


class VideoClaseAdmin(QualityModelAdmin):
    readonly_fields = ('group',)
    list_per_page = 20

admin.site.register(QualityControl)
admin.site.register(QualityItem)
admin.site.register(QualityScore)


admin_site.register(QualityControl, QualityModelAdmin)
admin_site.register(QualityItem, QualityModelAdmin)
admin_site.register(QualityScore, CustomModelAdmin)
admin_site.register(VideoClase, VideoClaseAdmin)
