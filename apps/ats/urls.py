from django.urls import path

from apps.ats import views


urlpatterns = [
    path('analyze/', views.analyze_resume_view, name='ats-analyze'),
    path('analyses/<int:analysis_id>/', views.analysis_detail_view, name='ats-analysis-detail'),
]
