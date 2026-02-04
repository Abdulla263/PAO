from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime
from django.core.validators import RegexValidator

# Create your models here.

NATIONALITY = [
    ('BH', 'Bahraini'),
    ('SA', 'Saudi'),
    ('KW', 'Kuwaiti'),
    ('AE', 'Emirati'),
    ('OM', 'Omani'),
    ('QA', 'Qatari'),
    ('OTHER', 'Other'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpr = models.CharField(
        max_length=9,
        validators=[RegexValidator(regex=r'^\d{9}$', message='CPR must be exactly 9 digits')],
        null=True
    )
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\d+$', message='Phone number must contain digits only')],
        blank=True
    )
    nationality = models.CharField(max_length=10, choices=NATIONALITY, null=True)

    def __str__(self):
        return self.user.username


class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=200)

    def __str__(self):
        return f"{self.title}"


class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Module {self.module.id} quiz by { self.user.username } on { self.timestamp }"


class Question(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="question")
    text = models.CharField()

    def __str__(self):
        return f"Module {self.module.id}: {self.text}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text}"


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s note at {self.timestamp}"
