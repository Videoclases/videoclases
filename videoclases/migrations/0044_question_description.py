# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0043_auto_20160627_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
