# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0027_auto_20150913_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='BooleanParameters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=256)),
                ('value', models.BooleanField()),
            ],
        ),
    ]
