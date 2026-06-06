def interview_question_prompt(role, difficulty, question_count):
    return f"""
Create {question_count} {difficulty} mock interview questions for a {role} candidate.
Return JSON only with this shape:
{{"questions": [{{"question": "...", "topic": "...", "expected_points": ["..."]}}]}}
"""


def interview_feedback_prompt(role, answers):
    return f"""
Evaluate these mock interview answers for a {role} candidate:
{answers}

Return JSON only with:
score, communication_score, correctness_score, confidence_score, strengths,
improvements, next_practice_topics, detailed_report, and video_tips.

Each detailed_report item must include:
area, mistake, why_it_matters, what_to_change, example_fix.
"""


def ats_prompt(resume_text, job_description):
    return f"""
Compare this resume against the job description and produce ATS feedback.

Resume:
{resume_text[:4000]}

Job description:
{job_description[:2500]}

Return JSON only with:
score, matched_keywords, missing_keywords, skill_gaps, formatting_issues,
improvement_suggestions, and detailed_report.

Each detailed_report item must include:
area, mistake, why_it_matters, what_to_change, example_fix.
"""


def study_plan_prompt(profile):
    return f"""
Create a personalized 7 day career prep study plan from this profile:
{profile}

Return JSON only with:
focus_summary, weekly_goal, days where each day has day, title, tasks,
practice_minutes, and checkpoint.
"""
