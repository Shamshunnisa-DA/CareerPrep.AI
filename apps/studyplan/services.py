from apps.common.constants import ROLE_SKILLS
from core.ai.gemini_client import GeminiClient
from core.ai.prompts import study_plan_prompt


def build_weak_topics(target_role, ats_missing=None, interview_topics=None):
    topics = []
    topics.extend(ats_missing or [])
    topics.extend(interview_topics or [])
    if not topics:
        topics = ROLE_SKILLS.get((target_role or '').lower(), ROLE_SKILLS['backend'])
    return list(dict.fromkeys(topics))[:8]


def generate_study_plan(target_role, ats_score=0, interview_score=0, weak_topics=None, days=7):
    days = min(max(int(days or 7), 3), 14)
    weak_topics = weak_topics or build_weak_topics(target_role)
    profile = {
        'target_role': target_role,
        'ats_score': ats_score,
        'interview_score': interview_score,
        'weak_topics': weak_topics,
        'days': days,
    }

    client = GeminiClient()
    ai_result = client.generate_json(study_plan_prompt(profile))
    if ai_result:
        return ai_result

    plan_days = []
    for index in range(days):
        topic = weak_topics[index % len(weak_topics)]
        plan_days.append({
            'day': index + 1,
            'title': f'{topic.title()} practice',
            'tasks': [
                f'Revise core concepts of {topic}.',
                f'Build or improve one mini example using {topic}.',
                f'Answer 3 interview questions related to {topic}.',
            ],
            'practice_minutes': 60 if index < 5 else 90,
            'checkpoint': 'Write a short summary of what improved and what is still unclear.',
        })

    if ats_score < 70:
        plan_days[0]['tasks'].append('Update resume bullets with role keywords and measurable outcomes.')
    if interview_score < 70:
        plan_days[min(1, len(plan_days) - 1)]['tasks'].append('Record one mock answer and review clarity, structure, and confidence.')

    return {
        'focus_summary': f'Improve {target_role} readiness by closing resume and interview gaps.',
        'weekly_goal': 'Raise ATS alignment and produce stronger technical interview answers.',
        'days': plan_days,
    }
