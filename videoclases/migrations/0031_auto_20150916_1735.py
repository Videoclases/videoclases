# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0030_auto_20150915_1845'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumno',
            name='changed_password',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profesor',
            name='changed_password',
            field=models.BooleanField(default=False),
        ),
    ]
