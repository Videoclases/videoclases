# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0039_auto_20160417_0241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentresponses',
            name='videoclase',
            field=models.ForeignKey(related_name='answers', to='videoclases.VideoClase'),
        ),
    ]
