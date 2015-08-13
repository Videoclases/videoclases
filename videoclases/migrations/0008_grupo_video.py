# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0007_auto_20150708_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupo',
            name='video',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
