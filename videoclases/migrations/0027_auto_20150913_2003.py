# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0026_auto_20150813_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profesor',
            name='cursos',
            field=models.ManyToManyField(to='videoclases.Curso', blank=True),
        ),
    ]
