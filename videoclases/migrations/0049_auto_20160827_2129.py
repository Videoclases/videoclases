# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0048_auto_20160827_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.ForeignKey(related_name='answer_question', to='videoclases.Alternative')),
                ('question', models.ForeignKey(related_name='response_question', to='videoclases.Question')),
            ],
        ),
        migrations.RemoveField(
            model_name='responses',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='responses',
            name='questions',
        ),
        migrations.AlterField(
            model_name='pedagogicalquestionsanswers',
            name='response',
            field=models.ManyToManyField(to='videoclases.Response'),
        ),
        migrations.AlterField(
            model_name='pedagogicalquestionsanswers',
            name='state',
            field=models.IntegerField(choices=[(1, b'Antes del envio de la tarea'), (2, b'Antes del la evaluaci\xc3\xb3n de videos'), (3, b'Despu\xc3\xa9s de la evaluaci\xc3\xb3n')]),
        ),
        migrations.DeleteModel(
            name='Responses',
        ),
    ]
