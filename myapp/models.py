from django.db import models
from django.contrib.auth.models import User

class Artifact(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    rarity = models.CharField(max_length=50)
    power = models.IntegerField()

    def __str__(self):
        return self.name