from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import Module, Quiz, Question, Answer


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
    return render(request, 'modules/quiz.html', {"module":module, "questions":questions})

def profile(request):
    return render(request, 'dash/profile.html')

