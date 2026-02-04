from django.urls import path , include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('modules/', views.modules, name='modules'),
    path('modules/<int:module_id>/', views.module_detail, name='detail'),

    path('modules/quiz/<int:module_id>/', views.quiz, name='quiz'),
    path('module/quiz/results/<int:quiz_id>/', views.quiz_results, name='quiz_results'),

    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/profile/edit/', views.ProfileEdit.as_view(), name='ProfileEdit')
]
