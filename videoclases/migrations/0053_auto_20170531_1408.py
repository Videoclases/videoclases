# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0052_auto_20170501_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videoclase',
            name='group',
            field=models.OneToOneField(null=True, blank=True, to='videoclases.GroupOfStudents'),
        ),
    ]
