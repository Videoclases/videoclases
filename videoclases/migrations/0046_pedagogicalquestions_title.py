# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0045_auto_20160703_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedagogicalquestions',
            name='title',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
