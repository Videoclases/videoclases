# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0037_auto_20160416_2304'),
    ]

    operations = [
        migrations.RenameModel('FinalNotes', 'FinalScores'),
    ]
