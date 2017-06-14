# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0055_videoclases_script'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentevaluations',
            name='comments',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
