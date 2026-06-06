from django.urls import path

from apps.studyplan import views


urlpatterns = [
    path('generate/', views.create_study_plan_view, name='study-plan-generate'),
    path('plans/<int:plan_id>/', views.study_plan_detail_view, name='study-plan-detail'),
]
