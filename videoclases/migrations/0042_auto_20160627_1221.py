# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0041_auto_20160609_1813'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='alternative_1',
        ),
        migrations.RemoveField(
            model_name='question',
            name='alternative_2',
        ),
        migrations.RemoveField(
            model_name='question',
            name='alternative_3',
        ),
        migrations.AddField(
            model_name='question',
            name='alternatives',
            field=models.ManyToManyField(related_name='question_alternatives', to='videoclases.Alternative'),
        ),
        migrations.AddField(
            model_name='question',
            name='correct',
            field=models.ForeignKey(related_name='question_correct', blank=True, to='videoclases.Alternative', null=True),
        ),
    ]
