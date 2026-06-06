from django.db import models
from django.conf import settings


class ResumeAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume_analyses', null=True, blank=True)
    candidate_name = models.CharField(max_length=120, blank=True)
    target_role = models.CharField(max_length=120)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    job_description = models.TextField()
    resume_text = models.TextField(blank=True)
    score = models.PositiveSmallIntegerField(default=0)
    matched_keywords = models.JSONField(default=list)
    missing_keywords = models.JSONField(default=list)
    skill_gaps = models.JSONField(default=list)
    formatting_issues = models.JSONField(default=list)
    improvement_suggestions = models.JSONField(default=list)
    detailed_report = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.target_role} ATS score: {self.score}'
