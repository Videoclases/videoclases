# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0023_auto_20150807_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='notasfinales',
            name='alumno',
            field=models.ForeignKey(default=1, to='videoclases.Alumno'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notasfinales',
            name='grupo',
            field=models.ForeignKey(to='videoclases.Grupo'),
        ),
    ]
