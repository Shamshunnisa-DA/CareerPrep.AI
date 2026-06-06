# Generated manually for the AI Career Prep Platform scaffold.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='InterviewSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=120)),
                ('difficulty', models.CharField(default='medium', max_length=20)),
                ('question_count', models.PositiveSmallIntegerField(default=5)),
                ('questions', models.JSONField(default=list)),
                ('answers', models.JSONField(default=list)),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('feedback', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
