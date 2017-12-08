# coding=utf-8
from django.db import models

from videoclases.models.teacher import Teacher
from videoclases.models.video_clase import VideoClase
from .quality_score import QualityScore


class QualityItem(models.Model):
    videoclase = models.ForeignKey(VideoClase, related_name='qualityItemList')
    score_check = models.ManyToManyField(QualityScore)
    teacher = models.ForeignKey(Teacher)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return u"{0}".format(self.videoclase.question[:50])

    def get_evaluation(self):
        if self.score_check.count() > 0:
            result = list()
            for c in self.score_check.select_related('criteria'):
                result.append(
                    {'id': c.criteria.id, 'name': c.criteria.value, 'value': c.score}
                )
            return result
        return []
