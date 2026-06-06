import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from apps.common.responses import error_response, success_response
from apps.interview.models import InterviewSession
from apps.interview.serializers import serialize_interview_session
from apps.interview.services import evaluate_answers, generate_questions


def json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@login_required
@require_POST
def start_interview_view(request):
    payload = json_body(request)
    role = (payload.get('role') or '').strip()
    difficulty = payload.get('difficulty', 'medium')
    question_count = payload.get('question_count', 5)
    if not role:
        return error_response('role is required', status=422)

    questions = generate_questions(role, difficulty, question_count)
    session = InterviewSession.objects.create(
        user=request.user,
        role=role,
        difficulty=difficulty,
        question_count=len(questions),
        questions=questions,
    )
    return success_response(serialize_interview_session(session), 'Interview session started', status=201)


@csrf_exempt
@login_required
@require_POST
def submit_interview_view(request, session_id):
    payload = json_body(request)
    answers = payload.get('answers', [])
    try:
        session = InterviewSession.objects.get(id=session_id, user=request.user)
    except InterviewSession.DoesNotExist:
        return error_response('Interview session not found', status=404)
    if not isinstance(answers, list) or not answers:
        return error_response('answers must be a non-empty list', status=422)

    result = evaluate_answers(session.role, session.questions, answers)
    session.answers = answers
    session.score = result['score']
    session.feedback = result['feedback']
    session.save(update_fields=['answers', 'score', 'feedback', 'updated_at'])
    return success_response(serialize_interview_session(session), 'Interview evaluated')


@login_required
@require_GET
def session_detail_view(request, session_id):
    try:
        session = InterviewSession.objects.get(id=session_id, user=request.user)
    except InterviewSession.DoesNotExist:
        return error_response('Interview session not found', status=404)
    return success_response(serialize_interview_session(session))
