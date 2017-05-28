# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0047_auto_20160827_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responses',
            name='questions',
            field=models.ForeignKey(to='videoclases.Question'),
        ),
    ]
