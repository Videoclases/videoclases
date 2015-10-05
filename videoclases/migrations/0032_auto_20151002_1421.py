# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0031_auto_20150916_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='cursos',
            field=models.ManyToManyField(related_name='alumnos', to='videoclases.Curso'),
        ),
    ]
