from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ats', '0002_resumeanalysis_detailed_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='resumeanalysis',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resume_analyses', to=settings.AUTH_USER_MODEL),
        ),
    ]
