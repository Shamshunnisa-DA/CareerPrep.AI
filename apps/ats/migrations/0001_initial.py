# Generated manually for the AI Career Prep Platform scaffold.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ResumeAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('candidate_name', models.CharField(blank=True, max_length=120)),
                ('target_role', models.CharField(max_length=120)),
                ('resume_file', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('job_description', models.TextField()),
                ('resume_text', models.TextField(blank=True)),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('matched_keywords', models.JSONField(default=list)),
                ('missing_keywords', models.JSONField(default=list)),
                ('skill_gaps', models.JSONField(default=list)),
                ('formatting_issues', models.JSONField(default=list)),
                ('improvement_suggestions', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
