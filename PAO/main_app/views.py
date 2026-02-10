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
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime

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
            first_part = salary * 0.0416 * 36
            remaining_months = months - 36
            second_part = salary * 0.0832 * remaining_months
            indemnity = first_part + second_part

    return render(request, 'calculator.html', {"indemnity": indemnity, "notify": notify})



@login_required
def generate_pdf_view(request, user_id):
    profile = Profile.objects.get(user__id=user_id)
    user = profile.user

    modules = Module.objects.all().order_by("id")

    module_scores = []
    for module in modules:
        quiz = Quiz.objects.filter(user=user, module=module).order_by('-timestamp').first()
        if quiz:
            total = quiz.responses.count()
            percentage = int((quiz.score / total) * 100) if total else 0
        else:
            percentage = 0
        module_scores.append((module.id, module.title, percentage))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter

    PRIMARY = HexColor("#17325A")
    CARD_BG = HexColor("#DDD6CA")
    TEXT_GRAY = HexColor("#374151")
    MUTED_GRAY = HexColor("#6b7280")

    # ================= TITLE (ABOVE HEADER) =================
    p.setFillColor(TEXT_GRAY)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(
        width / 2,
        height - 40,
        "Post-Arrival Orientation for Domestic Workers in the Kingdom of Bahrain"
    )

    y = height - 70

    # ================= HEADER =================
    p.setFillColor(PRIMARY)
    p.rect(0, y - 80, width, 80, fill=1)

    if profile.image:
        img = ImageReader(profile.image.path)
        p.drawImage(img, 40, y - 70, width=60, height=60, mask='auto')

    p.setFillColor(CARD_BG)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(120, y - 35, f"{user.first_name} {user.last_name}")
    p.setFont("Helvetica", 10)
    p.drawString(120, y - 55, "User Progress Report")

    y -= 120

    # ================= USER INFO CARD =================
    p.setFillColor(CARD_BG)
    p.rect(40, y - 120, width - 80, 120, fill=1, stroke=0)

    p.setFillColor(TEXT_GRAY)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(60, y - 30, "User Information")

    p.setFont("Helvetica", 10)
    info = [
        f"Email: {user.email}",
        f"Nationality: {profile.nationality}",
        f"Address: {profile.address}",
        f"CPR: {profile.cpr}",
    ]

    iy = y - 55
    for line in info:
        p.drawString(60, iy, line)
        iy -= 18

    y -= 160

    # ================= QUIZ SCORES =================
    p.setFillColor(CARD_BG)
    p.rect(40, y - 200, width - 80, 200, fill=1, stroke=0)

    p.setFillColor(TEXT_GRAY)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(60, y - 30, "Quiz Results")

    p.setFont("Helvetica", 10)
    sy = y - 60

    for module_id, title, score in module_scores:
        p.drawString(70, sy, f"Module {module_id}: {title}")
        p.drawRightString(width - 70, sy, f"{score}%")
        sy -= 18

        if sy < 80:
            p.showPage()
            sy = height - 100

    # ================= FOOTER =================
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    p.setFont("Helvetica", 8)
    p.setFillColor(MUTED_GRAY)

    p.drawCentredString(
        width / 2,
        50,
        "This report is a computer-generated document created at the request of the user."
    )
    p.drawCentredString(
        width / 2,
        35,
        f"Generated on: {timestamp}"
    )

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"{user.first_name}_report.pdf"
    )
