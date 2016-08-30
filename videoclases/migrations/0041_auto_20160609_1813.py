# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0040_auto_20160417_1235'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alternative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('response', models.CharField(max_length=255, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PedagogicalQuestions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('homework', models.OneToOneField(to='videoclases.Homework')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=255, null=True, blank=True)),
                ('alternative_1', models.CharField(max_length=255, null=True, blank=True)),
                ('alternative_2', models.CharField(max_length=255, null=True, blank=True)),
                ('alternative_3', models.CharField(max_length=255, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Responses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.ManyToManyField(to='videoclases.Alternative')),
                ('questions', models.ForeignKey(to='videoclases.PedagogicalQuestions')),
                ('student', models.ForeignKey(to='videoclases.Student')),
            ],
        ),
        migrations.AddField(
            model_name='pedagogicalquestions',
            name='questions',
            field=models.ManyToManyField(related_name='pedagogical_questions', to='videoclases.Question'),
        ),
    ]
