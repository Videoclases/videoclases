# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0019_auto_20150803_1212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evaluacionesdealumnos',
            name='grupo',
        ),
        migrations.AddField(
            model_name='evaluacionesdealumnos',
            name='videoclase',
            field=models.ForeignKey(related_name='evaluaciones', default=1, to='videoclases.VideoClase'),
            preserve_default=False,
        ),
    ]
