# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0014_auto_20150726_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupo',
            name='alumnos_subida',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
