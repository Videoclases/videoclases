# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoclases', '0052_auto_20170501_1823'),
    ]

    operations = [
        migrations.CreateModel(
            name='QualityControl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('homework', models.ManyToManyField(to='videoclases.Homework')),
            ],
        ),
        migrations.CreateModel(
            name='QualityItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='QualityScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field', models.CharField(max_length=200)),
                ('score', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='qualityitem',
            name='score_check',
            field=models.ManyToManyField(to='quality_control.QualityScore'),
        ),
        migrations.AddField(
            model_name='qualityitem',
            name='videoclase',
            field=models.ForeignKey(to='videoclases.VideoClase'),
        ),
        migrations.AddField(
            model_name='qualitycontrol',
            name='list_items',
            field=models.ManyToManyField(to='quality_control.QualityItem'),
        ),
    ]
