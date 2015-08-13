# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0018_auto_20150731_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grupo',
            name='tarea',
            field=models.ForeignKey(related_name='grupos', to='videoclases.Tarea'),
        ),
    ]
