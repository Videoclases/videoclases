# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0006_auto_20150708_2043'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='grupo',
            unique_together=set([('numero', 'tarea')]),
        ),
    ]
