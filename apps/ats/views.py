from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from apps.ats.models import ResumeAnalysis
from apps.ats.serializers import serialize_resume_analysis
from apps.ats.services import analyze_resume, extract_resume_text
from apps.common.responses import error_response, success_response


@csrf_exempt
@login_required
@require_POST
def analyze_resume_view(request):
    target_role = request.POST.get('target_role', '').strip()
    job_description = request.POST.get('job_description', '').strip()
    candidate_name = request.POST.get('candidate_name', '').strip()
    resume_file = request.FILES.get('resume')
    resume_text = request.POST.get('resume_text', '').strip() or extract_resume_text(resume_file)

    if not target_role or not job_description or not resume_text:
        return error_response(
            'target_role, job_description, and resume/resume_text are required.',
            status=422,
        )

    result = analyze_resume(resume_text, job_description, target_role)
    analysis = ResumeAnalysis.objects.create(
        user=request.user,
        candidate_name=candidate_name,
        target_role=target_role,
        resume_file=resume_file,
        job_description=job_description,
        resume_text=resume_text,
        **result,
    )
    return success_response(serialize_resume_analysis(analysis), 'ATS analysis completed', status=201)


@login_required
@require_GET
def analysis_detail_view(request, analysis_id):
    try:
        analysis = ResumeAnalysis.objects.get(id=analysis_id, user=request.user)
    except ResumeAnalysis.DoesNotExist:
        return error_response('ATS analysis not found', status=404)
    return success_response(serialize_resume_analysis(analysis))
