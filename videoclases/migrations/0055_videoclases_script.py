# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_homework(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    VideoClase = apps.get_model('videoclases', 'VideoClase')
    print VideoClase.objects.all().count()
    for v in VideoClase.objects.all():
        v.save()


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0054_videoclase_homework'),
    ]

    operations = [
        migrations.RunPython(add_homework),
    ]