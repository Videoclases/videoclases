# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0046_pedagogicalquestions_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='PedagogicalQuestionsAnswers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.IntegerField(choices=[(0, b'Antes del envio de la tarea'), (1, b'Antes del la evaluaci\xc3\xb3n de videos'), (2, b'Despu\xc3\xa9s de la evaluaci\xc3\xb3n')])),
            ],
        ),
        migrations.RemoveField(
            model_name='responses',
            name='student',
        ),
        migrations.AddField(
            model_name='pedagogicalquestionsanswers',
            name='response',
            field=models.ManyToManyField(to='videoclases.Responses'),
        ),
        migrations.AddField(
            model_name='pedagogicalquestionsanswers',
            name='student',
            field=models.ForeignKey(to='videoclases.Student'),
        ),
        migrations.AddField(
            model_name='pedagogicalquestionsanswers',
            name='test',
            field=models.ForeignKey(to='videoclases.PedagogicalQuestions'),
        ),
    ]
