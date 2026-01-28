from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=200)

    def __str__(self):
        return f"{self.title}"



