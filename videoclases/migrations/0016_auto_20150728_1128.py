# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0015_grupo_alumnos_subida'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoClase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('video', models.CharField(max_length=100, null=True, blank=True)),
                ('pregunta', models.CharField(max_length=100, null=True, blank=True)),
                ('alternativa_correcta', models.CharField(max_length=100, null=True, blank=True)),
                ('alternativa_2', models.CharField(max_length=100, null=True, blank=True)),
                ('alternativa_3', models.CharField(max_length=100, null=True, blank=True)),
                ('alumnos_subida', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='grupo',
            name='alternativa_2',
        ),
        migrations.RemoveField(
            model_name='grupo',
            name='alternativa_3',
        ),
        migrations.RemoveField(
            model_name='grupo',
            name='alternativa_correcta',
        ),
        migrations.RemoveField(
            model_name='grupo',
            name='alumnos_subida',
        ),
        migrations.RemoveField(
            model_name='grupo',
            name='pregunta',
        ),
        migrations.RemoveField(
            model_name='grupo',
            name='video',
        ),
        migrations.AddField(
            model_name='videoclase',
            name='grupo',
            field=models.OneToOneField(to='videoclases.Grupo'),
        ),
    ]
