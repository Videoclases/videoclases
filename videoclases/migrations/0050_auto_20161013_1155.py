# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0049_auto_20160827_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentevaluations',
            name='copyright',
            field=models.IntegerField(default=0, choices=[('No cumple el criterio', 0), ('Cumple parcialmente el criterio', 0.5), ('Cumple el criterio', 1)]),
        ),
        migrations.AddField(
            model_name='studentevaluations',
            name='format',
            field=models.IntegerField(default=0, choices=[('No cumple el criterio', 0), ('Cumple parcialmente el criterio', 0.5), ('Cumple el criterio', 1)]),
        ),
        migrations.AddField(
            model_name='studentevaluations',
            name='originality',
            field=models.IntegerField(default=0, choices=[('No cumple el criterio', 0), ('Cumple parcialmente el criterio', 0.5), ('Cumple el criterio', 1)]),
        ),
        migrations.AddField(
            model_name='studentevaluations',
            name='pedagogical',
            field=models.IntegerField(default=0, choices=[('No cumple el criterio', 0), ('Cumple parcialmente el criterio', 0.5), ('Cumple el criterio', 1)]),
        ),
        migrations.AddField(
            model_name='studentevaluations',
            name='rythm',
            field=models.IntegerField(default=0, choices=[('No cumple el criterio', 0), ('Cumple parcialmente el criterio', 0.5), ('Cumple el criterio', 1)]),
        ),
        migrations.AddField(
            model_name='studentevaluations',
            name='theme',
            field=models.IntegerField(default=0, choices=[('No cumple el criterio', 0), ('Cumple parcialmente el criterio', 0.5), ('Cumple el criterio', 1)]),
        ),
        migrations.AlterField(
            model_name='pedagogicalquestionsanswers',
            name='state',
            field=models.IntegerField(choices=[(1, 'Antes del envio de la tarea'), (2, 'Antes del la evaluaci\xf3n de videos'), (3, 'Despu\xe9s de la evaluaci\xf3n')]),
        ),
        migrations.AlterField(
            model_name='studentevaluations',
            name='value',
            field=models.IntegerField(default=0, choices=[('No cumple el criterio', 0), ('Cumple parcialmente el criterio', 0.5), ('Cumple el criterio', 1)]),
        ),
    ]
