from django.contrib import admin

from apps.studyplan.models import StudyPlan


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ('target_role', 'ats_score', 'interview_score', 'created_at')
    search_fields = ('target_role',)
