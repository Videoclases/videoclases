# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0002_auto_20150708_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='profesor',
            name='cursos',
            field=models.ManyToManyField(to='videoclases.Curso'),
        ),
    ]
