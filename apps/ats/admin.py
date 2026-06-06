from django.contrib import admin

from apps.ats.models import ResumeAnalysis


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('target_role', 'candidate_name', 'score', 'created_at')
    search_fields = ('target_role', 'candidate_name', 'job_description')
    list_filter = ('target_role', 'created_at')
