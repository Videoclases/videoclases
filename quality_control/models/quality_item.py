# coding=utf-8
from django.db import models

from .quality_score import QualityScore
from videoclases.models.video_clase import VideoClase


class QualityItem(models.Model):
    videoclase = models.ForeignKey(VideoClase)
    score_check = models.ManyToManyField(QualityScore)

    def __unicode__(self):
        return "{0}".format(self.videoclase.question)