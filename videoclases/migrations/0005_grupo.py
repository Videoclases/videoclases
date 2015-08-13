# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0004_auto_20150708_1851'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.IntegerField()),
                ('alumnos', models.ManyToManyField(to='videoclases.AlumnoCurso')),
                ('tarea', models.ForeignKey(to='videoclases.Tarea')),
            ],
        ),
    ]
