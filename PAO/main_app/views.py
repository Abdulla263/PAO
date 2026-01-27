from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth import login
from .forms import CustomUserCreationForm
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
