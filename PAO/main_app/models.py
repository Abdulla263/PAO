from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime
from django.core.validators import RegexValidator
import json
import os
from django.conf import settings


# Define the path to your JSON file
json_file_path = os.path.join(settings.BASE_DIR, 'main_app', 'countries.json')

# Load the JSON data into a variable
with open(json_file_path, 'r') as file:
    nationalities_data = json.load(file)

# Create the choices from the loaded data
countries = [(country[0], country[1]) for country in nationalities_data['NATIONALITY']]

# Create your models here.

# NATIONALITY = [
#     ('BH', 'Bahraini'),
#     ('SA', 'Saudi'),
#     ('KW', 'Kuwaiti'),
#     ('AE', 'Emirati'),
#     ('OM', 'Omani'),
#     ('QA', 'Qatari'),
#     ('OTHER', 'Other'),
# ]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpr = models.CharField(
        max_length=9,
        validators=[RegexValidator(regex=r'^\d{9}$', message='CPR must be exactly 9 digits')],
        null=True,
        unique=True,
    )
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\d+$', message='Phone number must contain digits only')],
        blank=True
    )
    nationality = models.CharField(max_length=20, choices=countries, null=True)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.user.username


class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=200)

    def __str__(self):
        return f"{self.title}"


class Question(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="question")
    text = models.TextField()

    def __str__(self):
        return f"Module {self.module.id}: {self.text}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text}"


class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Module {self.module.id} quiz by { self.user.username } on { self.timestamp }"


class QuizAnswer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.quiz.user} | Module {self.quiz.module.id}: Q.{self.question.id} {'✅' if self.is_correct else '❌'} | {self.quiz.timestamp}"


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s note at {self.timestamp}"
