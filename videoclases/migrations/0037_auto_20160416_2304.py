# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0036_auto_20160416_2247'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='usuario',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='studentevaluations',
            old_name='autor',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='studentevaluations',
            old_name='valor',
            new_name='value',
        ),
        migrations.RenameField(
            model_name='studentresponses',
            old_name='respuesta',
            new_name='answer',
        ),
        migrations.RenameField(
            model_name='teacher',
            old_name='cursos',
            new_name='courses',
        ),
        migrations.RenameField(
            model_name='teacher',
            old_name='usuario',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='videoclase',
            old_name='alternativa_2',
            new_name='alternative_2',
        ),
        migrations.RenameField(
            model_name='videoclase',
            old_name='alternativa_3',
            new_name='alternative_3',
        ),
        migrations.RenameField(
            model_name='videoclase',
            old_name='alternativa_correcta',
            new_name='correct_alternative',
        ),
        migrations.RenameField(
            model_name='videoclase',
            old_name='pregunta',
            new_name='question',
        ),
        migrations.RenameField(
            model_name='videoclase',
            old_name='alumnos_subida',
            new_name='upload_students',
        ),
        migrations.RemoveField(
            model_name='student',
            name='cursos',
        ),
        migrations.AddField(
            model_name='student',
            name='courses',
            field=models.ManyToManyField(related_name='students', to='videoclases.Course'),
        ),
        migrations.AlterField(
            model_name='studentevaluations',
            name='videoclase',
            field=models.ForeignKey(related_name='evaluations', to='videoclases.VideoClase'),
        ),
    ]
