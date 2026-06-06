# Generated manually for the AI Career Prep Platform scaffold.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='StudyPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_role', models.CharField(max_length=120)),
                ('ats_score', models.PositiveSmallIntegerField(default=0)),
                ('interview_score', models.PositiveSmallIntegerField(default=0)),
                ('weak_topics', models.JSONField(default=list)),
                ('plan', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
