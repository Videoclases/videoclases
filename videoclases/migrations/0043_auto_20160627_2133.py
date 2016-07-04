# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0042_auto_20160627_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homework',
            name='course',
            field=models.ForeignKey(related_name='course_homework', to='videoclases.Course'),
        ),
    ]
