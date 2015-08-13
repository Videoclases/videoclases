# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0011_evaluacionesdealumnos_notasfinales'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notasfinales',
            name='grupo',
            field=models.OneToOneField(to='videoclases.Grupo'),
        ),
    ]
