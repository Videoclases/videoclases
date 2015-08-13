# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0021_auto_20150803_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notasfinales',
            name='nota_clase',
            field=models.FloatField(default=0, null=True, blank=True),
        ),
    ]
