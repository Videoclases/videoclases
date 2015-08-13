# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0012_auto_20150721_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarea',
            name='profesor',
            field=models.ForeignKey(default=1, to='videoclases.Profesor'),
            preserve_default=False,
        ),
    ]
