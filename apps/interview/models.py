from django.db import models
from django.conf import settings


class InterviewSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interview_sessions', null=True, blank=True)
    role = models.CharField(max_length=120)
    difficulty = models.CharField(max_length=20, default='medium')
    question_count = models.PositiveSmallIntegerField(default=5)
    questions = models.JSONField(default=list)
    answers = models.JSONField(default=list)
    score = models.PositiveSmallIntegerField(default=0)
    feedback = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.role} interview ({self.difficulty})'
