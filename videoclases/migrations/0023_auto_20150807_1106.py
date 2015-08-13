# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0022_auto_20150805_1532'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alumno',
            name='curso',
        ),
        migrations.AddField(
            model_name='alumno',
            name='cursos',
            field=models.ManyToManyField(to='videoclases.Curso'),
        ),
    ]
