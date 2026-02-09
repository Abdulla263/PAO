from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from .forms import CustomUserCreationForm, ProfileForm, QuestionForm, AnswerFormSet
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Module, Profile, Quiz, Question, Answer, QuizAnswer , Note
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

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

@login_required
def dashboard(request):
    modules = Module.objects.all().order_by("id")
    total_percentage=0

# getting the percentage in dash
    for module in modules:
        quiz = Quiz.objects.filter(user=request.user, module=module).order_by('-timestamp').first()
        if quiz:
            total_questions = quiz.responses.count()
            module.percentage = int((quiz.score/total_questions)*100)
        else:
            module.percentage = 0

        total_percentage = total_percentage + module.percentage

    total_progress = int(total_percentage/7)

# notes function
    if request.method == "POST":
        title = request.POST.get("title")
        text = request.POST.get("text")
        if title and text:
            Note.objects.create(user=request.user, title=title, text=text)
            return redirect('dashboard')
    notes = Note.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, 'dash/dashboard.html', {"modules":modules, "total_progress":total_progress, 'notes': notes})



def modules(request):
    modules = Module.objects.all().order_by("id")
    return render(request, 'modules/modules.html', {"modules": modules})

def module_detail(request, module_id):
    module = Module.objects.get(id=module_id)
    return render(request, f'modules/module{module_id}.html', {"module": module})

@login_required
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

@login_required
def quiz_results(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    responses = quiz.responses.select_related("question", "selected_answer")
    total = responses.count()
    percentage = int((quiz.score / total)*100)

    return render(request, 'modules/quiz_results.html', {
        "quiz": quiz,
        "module": quiz.module,
        "responses": responses,
        "total": total,
        "percentage": percentage,
        })



class QuestionUpdateView(LoginRequiredMixin,UpdateView):
    model = Question
    form_class = QuestionForm

    @login_required
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = AnswerFormSet(instance=self.object)
        return context

    @login_required
    def form_valid(self, form):
        formset = AnswerFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            self.object = form.save()
            formset.save()
            return redirect("quiz", module_id=self.object.module.id)
        return self.form_invalid(form)

class QuestionDeleteView(LoginRequiredMixin,DeleteView):
    model = Question

    @login_required
    def get_success_url(self):
        return reverse_lazy("quiz", kwargs={"module_id": self.object.module.id})


@login_required
def profile(request):
    return render(request, 'dash/profile.html')

class ProfileEdit(LoginRequiredMixin,UpdateView):
    model = Profile
    fields= ['cpr','phone','nationality','address','image']
    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

    def get_success_url(self):
        return '/dashboard/'



class CreateNote(LoginRequiredMixin,CreateView):
    model = Note
    fields = ['title','text']
    success_url = 'dashboard/'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class UpdateNote(LoginRequiredMixin,UpdateView):
    model = Note
    fields = ['title','text']
    success_url = '/dashboard/'

class DeleteNote(LoginRequiredMixin,DeleteView):
    model = Note
    success_url = '/dashboard/'


def calculator(request):
    indemnity = 0
    notify = ""

    if request.method == "POST":
        salary = float(request.POST.get('salary'))
        months = int(request.POST.get('months'))

        if months < 12:
            notify = "Only employees who have completed at least one year of continuous service are entitled to the indemnity."
        elif months <= 36:
            indemnity = salary * 0.0416 * months
        else:
            indemnity = (salary * 0.416 * 36) + (salary * 0.0832) * (months - 36)

    return render(request, 'calculator.html', {"indemnity": indemnity, "notify": notify})



@login_required
def generate_pdf_view(request, user_id):
    try:
        profile = Profile.objects.get(user__id=user_id)
    except Profile.DoesNotExist:
        return HttpResponse("Profile not found for this user", status=404)

    user = profile.user

    # Fetch all modules
    modules = Module.objects.all().order_by("id")

    # Prepare module scores (last quiz for this user)
    module_scores = []
    for module in modules:
        quiz = Quiz.objects.filter(user=user, module=module).order_by('-timestamp').first()
        if quiz:
            total_questions = quiz.responses.count()
            percentage = int((quiz.score / total_questions) * 100) if total_questions > 0 else 0
        else:
            percentage = 0
        module_scores.append((module.title, percentage))

    # Create PDF buffer
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    y = 750

    # Draw profile image if exists
    if profile.image:
        try:
            # Resize image to 80x80 and place at (100, y-80)
            img = ImageReader(profile.image.path)
            p.drawImage(img, 100, y - 80, width=80, height=80)
        except Exception as e:
            print("Error loading image:", e)

    # Shift text to the right if image is there
    text_x = 200 if profile.image else 100

    # Header: user info
    p.drawString(text_x, y, f"Hello {user.first_name} {user.last_name}, This is your report")
    y -= 20
    p.drawString(text_x, y, f"Email: {user.email}")
    y -= 20
    p.drawString(text_x, y, f"Nationality: {profile.nationality}")
    y -= 20
    p.drawString(text_x, y, f"Address: {profile.address}")
    y -= 20
    p.drawString(text_x, y, f"CPR: {profile.cpr}")
    y -= 40

    # Module quiz scores
    p.drawString(text_x, y, "Your Quiz Scores:")
    y -= 20
    for title, score in module_scores:
        p.drawString(text_x + 20, y, f"{title}: {score}%")
        y -= 20
        if y < 50:
            p.showPage()
            y = 750

    # Close PDF
    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f'{user.first_name}_report.pdf')

