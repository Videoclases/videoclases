# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0032_auto_20151002_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarea',
            name='titulo',
            field=models.CharField(max_length=80),
        ),
    ]
