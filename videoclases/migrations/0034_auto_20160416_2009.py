# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0033_auto_20151015_1803'),
    ]

    operations = [
        migrations.RenameModel('Alumno', 'Student'),
    ]
