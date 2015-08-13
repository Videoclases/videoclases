# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('videoclases', '0005_grupo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('curso', models.ForeignKey(to='videoclases.Curso')),
                ('usuario', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='alumnocurso',
            name='curso',
        ),
        migrations.RemoveField(
            model_name='alumnocurso',
            name='usuario',
        ),
        migrations.AlterField(
            model_name='grupo',
            name='alumnos',
            field=models.ManyToManyField(to='videoclases.Alumno'),
        ),
        migrations.DeleteModel(
            name='AlumnoCurso',
        ),
    ]
