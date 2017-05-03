# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0051_auto_20161016_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='homework',
            name='homework_to_evaluate',
            field=models.ForeignKey(blank=True, to='videoclases.Homework', null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='year',
            field=models.IntegerField(default=2017),
        ),
    ]
