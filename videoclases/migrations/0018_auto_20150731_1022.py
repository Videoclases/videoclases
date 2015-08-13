# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0017_respuestasdealumnos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluacionesdealumnos',
            name='valor',
            field=models.IntegerField(default=0),
        ),
    ]
