import json
from django.core.serializers import serialize
from django.core.management import BaseCommand

from videoclases.models.video_clase import VideoClase


class Command(BaseCommand):

    def handle(self, *args, **options):
        videosclases = VideoClase.objects.all().exclude(video__isnull=True)

        result = []
        for videosclase in videosclases:
            hw = videosclase.group.homework
            result.append(u", ".join([videosclase.video,hw.title,hw.course.name,str(hw.course.year)]))

        return json.dumps(result, indent=4)
