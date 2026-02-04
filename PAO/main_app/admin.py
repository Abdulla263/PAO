from django.contrib import admin
from .models import Module,Profile, Quiz, Question, Answer


class AnswerInLine(admin.TabularInline):
    model = Answer
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInLine]

# Register your models here.

admin.site.register(Module)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Profile)


