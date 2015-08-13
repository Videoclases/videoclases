# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0013_tarea_profesor'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupo',
            name='alternativa_2',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='grupo',
            name='alternativa_3',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='grupo',
            name='alternativa_correcta',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='grupo',
            name='pregunta',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
