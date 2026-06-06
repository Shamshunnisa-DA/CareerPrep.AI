"""
URL configuration for careerprep project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import include, path

from apps.ats.models import ResumeAnalysis
from apps.ats.serializers import serialize_resume_analysis
from apps.common.responses import success_response
from apps.interview.models import InterviewSession
from apps.interview.serializers import serialize_interview_session
from apps.studyplan.models import StudyPlan
from apps.studyplan.serializers import serialize_study_plan

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {
        'recent_ats': ResumeAnalysis.objects.filter(user=request.user)[:5],
        'recent_interviews': InterviewSession.objects.filter(user=request.user)[:5],
        'recent_plans': StudyPlan.objects.filter(user=request.user)[:5],
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')
    return render(request, 'auth.html', {
        'form': form,
        'mode': 'login',
        'title': 'Welcome back',
        'button_text': 'Login',
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'auth.html', {
        'form': form,
        'mode': 'register',
        'title': 'Create your account',
        'button_text': 'Create Account',
    })


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def report_history(request):
    return success_response({
        'ats': [serialize_resume_analysis(item) for item in ResumeAnalysis.objects.filter(user=request.user)[:10]],
        'interviews': [serialize_interview_session(item) for item in InterviewSession.objects.filter(user=request.user)[:10]],
        'plans': [serialize_study_plan(item) for item in StudyPlan.objects.filter(user=request.user)[:10]],
    })


def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'project': 'AI Career Prep Platform',
        'modules': ['ats', 'interview', 'studyplan'],
    })

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/reports/history/', report_history, name='report-history'),
    path('api/ats/', include('apps.ats.urls')),
    path('api/interview/', include('apps.interview.urls')),
    path('api/study-plan/', include('apps.studyplan.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
