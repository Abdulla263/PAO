from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.urls import reverse , reverse_lazy
from .forms import CustomUserCreationForm , ProfileForm
from django.views.generic.edit import UpdateView
from .models import Module, Profile, Quiz, Question, Answer, QuizAnswer




# Create your views here.
def signup(request):
    error_message = ''

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('about')
        else:
            error_message = 'Invalid signup - try again'
    else:
        form = CustomUserCreationForm()

    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def dashboard(request):
    return render(request, 'dash/dashboard.html')

def modules(request):
    modules = Module.objects.all().order_by("id")
    return render(request, 'modules/modules.html', {"modules": modules})

def module_detail(request, module_id):
    module = Module.objects.get(id=module_id)
    return render(request, f'modules/module{module_id}.html', {"module": module})


def quiz(request, module_id):
    module = Module.objects.get(id=module_id)
    questions = Question.objects.filter(module=module).order_by("?")

    if request.method == "POST":
        score = 0

        quiz_attempt = Quiz.objects.create(
            user=request.user,
            module=module,
            score=0,
            )

        for question in questions:
            selected_answer_id = request.POST.get(f"question_{question.id}")
            selected_answer = Answer.objects.get(id=selected_answer_id)
            correct_answer = question.answers.get(is_correct=True)

            is_correct = selected_answer == correct_answer
            if is_correct:
                score = score+1

            QuizAnswer.objects.create(
                quiz=quiz_attempt,
                question=question,
                selected_answer=selected_answer,
                is_correct=is_correct
            )

        quiz_attempt.score = score
        quiz_attempt.save()

        return redirect("quiz_results", quiz_id=quiz_attempt.id)

    return render(request, 'modules/quiz.html', {"module":module, "questions":questions})


def quiz_results(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    responses = quiz.responses.select_related("question", "selected_answer")
    total = responses.count()

    return render(request, 'modules/quiz_results.html', {
        "quiz": quiz,
        "module": quiz.module,
        "responses": responses,
        "total": total,
        })



def profile(request):
    return render(request, 'dash/profile.html')

class ProfileEdit(UpdateView):
    model = Profile
    fields= ['cpr','phone','nationality']
    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

    def get_success_url(self):
        return '/accounts/profile/'



