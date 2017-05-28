import json
from django.core.serializers import serialize
from django.core.management import BaseCommand

from videoclases.models.video_clase import VideoClase


class Command(BaseCommand):

    def handle(self, *args, **options):
        videosclases = VideoClase.objects.all().exclude(video__isnull=True)

        result = []
        for videosclase in videosclases:
            result.append(videosclase.video)

        return json.dumps(result, indent=4)
