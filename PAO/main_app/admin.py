from django.contrib import admin
from .models import Module, Quiz, Question, Answer

# Register your models here.

admin.site.register(Module)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
