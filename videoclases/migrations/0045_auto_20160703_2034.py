# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from datetime import timedelta
class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0044_question_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='description',
        ),
        migrations.AddField(
            model_name='pedagogicalquestions',
            name='delta_time',
            field=models.DurationField(default=timedelta),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pedagogicalquestions',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
