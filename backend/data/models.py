from django.db import models


class User(models.Model):
    tg_id = models.PositiveBigIntegerField(unique=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=3, default='uz')

    def __str__(self):
        return self.full_name
