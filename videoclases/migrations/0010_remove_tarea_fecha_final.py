# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0009_auto_20150714_1613'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarea',
            name='fecha_final',
        ),
    ]
