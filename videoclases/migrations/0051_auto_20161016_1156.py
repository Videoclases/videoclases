# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0050_auto_20161013_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentevaluations',
            name='copyright',
            field=models.DecimalField(default=0, max_digits=2, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='studentevaluations',
            name='format',
            field=models.DecimalField(default=0, max_digits=2, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='studentevaluations',
            name='originality',
            field=models.DecimalField(default=0, max_digits=2, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='studentevaluations',
            name='pedagogical',
            field=models.DecimalField(default=0, max_digits=2, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='studentevaluations',
            name='rythm',
            field=models.DecimalField(default=0, max_digits=2, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='studentevaluations',
            name='theme',
            field=models.DecimalField(default=0, max_digits=2, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='studentevaluations',
            name='value',
            field=models.IntegerField(default=0),
        ),
    ]
