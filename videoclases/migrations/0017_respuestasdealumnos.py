# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0016_auto_20150728_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='RespuestasDeAlumnos',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('respuesta', models.CharField(max_length=100, null=True, blank=True)),
                ('alumno', models.ForeignKey(to='videoclases.Alumno')),
                ('videoclase', models.ForeignKey(to='videoclases.VideoClase')),
            ],
        ),
    ]
