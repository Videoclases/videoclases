# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0008_grupo_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarea',
            name='fecha_evaluacion',
            field=models.DateField(default=datetime.datetime(datetime.date.today().year, 7, 14, 19, 13, 37, 829193, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tarea',
            name='fecha_final',
            field=models.DateField(default=datetime.datetime(datetime.date.today().year, 7, 14, 19, 13, 42, 94949, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tarea',
            name='fecha_subida',
            field=models.DateField(default=datetime.datetime(datetime.date.today().year, 7, 14, 19, 13, 46, 251368, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
