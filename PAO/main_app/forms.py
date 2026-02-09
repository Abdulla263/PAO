from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Question, Answer
from django.forms import inlineformset_factory

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2',
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['cpr', 'phone', 'nationality', 'address', 'image']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text"]


AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    fields=("text", "is_correct"),
    extra=0,
    can_delete=True
)
