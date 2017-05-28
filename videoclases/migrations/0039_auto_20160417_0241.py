# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0038_auto_20160416_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupofstudents',
            name='homework',
            field=models.ForeignKey(related_name='groups', to='videoclases.Homework'),
        ),
    ]
