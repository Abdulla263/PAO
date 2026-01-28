from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
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
class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=200)

    def __str__(self):
        return f"{self.title}"


from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
cpr = models.CharField(
        max_length=9,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{9}$',message='CPR must be exactly 9 digits')])
phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\d+$',message='Phone number must contain digits only')],blank=True)
image = models.ImageField(upload_to='main_app/static/uploads/', default='')
nationality = models.CharField(max_length=10,choices=NATIONALITY)

def __str__(self):
        return self.user.username

