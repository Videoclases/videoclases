# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0010_remove_tarea_fecha_final'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluacionesDeAlumnos',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor', models.IntegerField()),
                ('autor', models.ForeignKey(to='videoclases.Alumno')),
                ('grupo', models.ForeignKey(to='videoclases.Grupo')),
            ],
        ),
        migrations.CreateModel(
            name='NotasFinales',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nota_clase', models.FloatField(default=0)),
                ('nota_profesor', models.FloatField(default=0)),
                ('grupo', models.ForeignKey(to='videoclases.Grupo')),
            ],
        ),
    ]
