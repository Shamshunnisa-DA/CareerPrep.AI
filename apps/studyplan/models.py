from django.db import models
from django.conf import settings


class StudyPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_plans', null=True, blank=True)
    target_role = models.CharField(max_length=120)
    ats_score = models.PositiveSmallIntegerField(default=0)
    interview_score = models.PositiveSmallIntegerField(default=0)
    weak_topics = models.JSONField(default=list)
    plan = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.target_role} study plan'
