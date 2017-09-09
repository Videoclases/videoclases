from django.db import models


class Alternative(models.Model):
    response = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.response
