# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0020_auto_20150803_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='respuestasdealumnos',
            name='videoclase',
            field=models.ForeignKey(related_name='respuestas', to='videoclases.VideoClase'),
        ),
    ]
