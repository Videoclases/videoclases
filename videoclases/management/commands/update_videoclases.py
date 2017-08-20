from django.core.management import BaseCommand

from videoclases.models.video_clase import VideoClase


class Command(BaseCommand):

    def handle(self, *args, **options):
        i = 0
        for v in VideoClase.objects.all():
            v.save()
            i += 1
        print(u"Finished, total "+str(i))
