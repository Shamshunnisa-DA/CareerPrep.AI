from django.urls import path

from apps.interview import views


urlpatterns = [
    path('start/', views.start_interview_view, name='interview-start'),
    path('sessions/<int:session_id>/', views.session_detail_view, name='interview-session-detail'),
    path('sessions/<int:session_id>/submit/', views.submit_interview_view, name='interview-submit'),
]
