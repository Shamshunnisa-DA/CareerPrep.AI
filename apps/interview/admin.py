from django.contrib import admin

from apps.interview.models import InterviewSession


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('role', 'difficulty', 'score', 'created_at')
    search_fields = ('role',)
    list_filter = ('difficulty', 'created_at')
