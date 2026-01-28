from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime


# Create your models here.

class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=200)

    def __str__(self):
        return f"{self.title}"


class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module.id}. {self.module.title} quiz by { self.user.username }"


class Question(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    text = models.CharField()

    def __str__(self):
        return f"{self.text}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text}"

