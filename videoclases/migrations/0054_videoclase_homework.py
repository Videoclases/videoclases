# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0053_auto_20170531_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='videoclase',
            name='homework',
            field=models.ForeignKey(blank=True, to='videoclases.Homework', null=True),
        ),
    ]
