import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from apps.ats.models import ResumeAnalysis
from apps.common.responses import error_response, success_response
from apps.interview.models import InterviewSession
from apps.studyplan.models import StudyPlan
from apps.studyplan.serializers import serialize_study_plan
from apps.studyplan.services import build_weak_topics, generate_study_plan


def json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@login_required
@require_POST
def create_study_plan_view(request):
    payload = json_body(request)
    target_role = (payload.get('target_role') or '').strip()
    ats_score = int(payload.get('ats_score') or 0)
    interview_score = int(payload.get('interview_score') or 0)
    weak_topics = payload.get('weak_topics') or []

    ats_id = payload.get('ats_analysis_id')
    if ats_id:
        try:
            analysis = ResumeAnalysis.objects.get(id=ats_id, user=request.user)
            target_role = target_role or analysis.target_role
            ats_score = analysis.score
            weak_topics = build_weak_topics(target_role, analysis.missing_keywords, weak_topics)
        except ResumeAnalysis.DoesNotExist:
            return error_response('ATS analysis not found', status=404)

    interview_id = payload.get('interview_session_id')
    if interview_id:
        try:
            interview = InterviewSession.objects.get(id=interview_id, user=request.user)
            target_role = target_role or interview.role
            interview_score = interview.score
            weak_topics = build_weak_topics(
                target_role,
                weak_topics,
                interview.feedback.get('next_practice_topics', []),
            )
        except InterviewSession.DoesNotExist:
            return error_response('Interview session not found', status=404)

    if not target_role:
        return error_response('target_role is required', status=422)

    plan = generate_study_plan(
        target_role=target_role,
        ats_score=ats_score,
        interview_score=interview_score,
        weak_topics=weak_topics,
        days=payload.get('days', 7),
    )
    study_plan = StudyPlan.objects.create(
        user=request.user,
        target_role=target_role,
        ats_score=ats_score,
        interview_score=interview_score,
        weak_topics=weak_topics,
        plan=plan,
    )
    return success_response(serialize_study_plan(study_plan), 'Study plan generated', status=201)


@login_required
@require_GET
def study_plan_detail_view(request, plan_id):
    try:
        study_plan = StudyPlan.objects.get(id=plan_id, user=request.user)
    except StudyPlan.DoesNotExist:
        return error_response('Study plan not found', status=404)
    return success_response(serialize_study_plan(study_plan))
