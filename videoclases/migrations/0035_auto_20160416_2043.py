# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0034_auto_20160416_2009'),
    ]

    operations = [
        migrations.RenameModel('Curso', 'Course'),
        migrations.RenameModel('NotasFinales', 'FinalNotes'),
#        migrations.RenameModel('FinalNotes', 'FinalNotes'),
        migrations.RenameModel('Grupo', 'GroupOfStudents'),
        migrations.RenameModel('Tarea', 'Homework'),
        migrations.RenameModel('Colegio', 'School'),
        migrations.RenameModel('EvaluacionesDeAlumnos', 'StudentEvaluations'),
        migrations.RenameModel('RespuestasDeAlumnos', 'StudentResponses'),
        migrations.RenameModel('Profesor', 'Teacher'),
        ]