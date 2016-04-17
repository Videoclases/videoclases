# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0035_auto_20160416_2043'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='nombre',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='course',
            old_name='colegio',
            new_name='school',
        ),
        migrations.RenameField(
            model_name='course',
            old_name='anho',
            new_name='year',
        ),
        migrations.RenameField(
            model_name='finalnotes',
            old_name='nota_clase',
            new_name='class_score',
        ),
        migrations.RenameField(
            model_name='finalnotes',
            old_name='grupo',
            new_name='group',
        ),
        migrations.RenameField(
            model_name='finalnotes',
            old_name='alumno',
            new_name='student',
        ),
        migrations.RenameField(
            model_name='finalnotes',
            old_name='nota_profesor',
            new_name='teacher_score',
        ),
        migrations.RenameField(
            model_name='groupofstudents',
            old_name='tarea',
            new_name='homework',
        ),
        migrations.RenameField(
            model_name='groupofstudents',
            old_name='numero',
            new_name='number',
        ),
        migrations.RenameField(
            model_name='groupofstudents',
            old_name='alumnos',
            new_name='students',
        ),
        migrations.RenameField(
            model_name='homework',
            old_name='curso',
            new_name='course',
        ),
        migrations.RenameField(
            model_name='homework',
            old_name='fecha_evaluacion',
            new_name='date_evaluation',
        ),
        migrations.RenameField(
            model_name='homework',
            old_name='fecha_subida',
            new_name='date_upload',
        ),
        migrations.RenameField(
            model_name='homework',
            old_name='descripcion',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='homework',
            old_name='revisiones',
            new_name='revision',
        ),
        migrations.RenameField(
            model_name='homework',
            old_name='profesor',
            new_name='teacher',
        ),
        migrations.RenameField(
            model_name='homework',
            old_name='titulo',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='school',
            old_name='nombre',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='studentresponses',
            old_name='alumno',
            new_name='student',
        ),
        migrations.RenameField(
            model_name='teacher',
            old_name='colegio',
            new_name='school',
        ),
        migrations.RenameField(
            model_name='videoclase',
            old_name='grupo',
            new_name='group',
        ),
        migrations.AlterUniqueTogether(
            name='groupofstudents',
            unique_together=set([('number', 'homework')]),
        ),
    ]
