import re

from apps.common.constants import DEFAULT_SKILLS, ROLE_SKILLS
from core.ai.gemini_client import GeminiClient
from core.ai.prompts import ats_prompt


WORD_PATTERN = re.compile(r'[a-zA-Z][a-zA-Z+#.\-]{1,}')


def extract_resume_text(uploaded_file):
    if not uploaded_file:
        return ''

    raw = uploaded_file.read()
    uploaded_file.seek(0)
    try:
        return raw.decode('utf-8', errors='ignore')
    except AttributeError:
        return str(raw)


def normalize_words(text):
    return {word.lower().strip('.-,') for word in WORD_PATTERN.findall(text or '')}


def expected_keywords(target_role, job_description):
    role_key = (target_role or '').strip().lower()
    base = set(ROLE_SKILLS.get(role_key, DEFAULT_SKILLS))
    jd_words = normalize_words(job_description)
    useful_jd_words = {
        word for word in jd_words
        if len(word) > 3 and word not in {'with', 'from', 'that', 'this', 'will', 'have', 'your'}
    }
    return sorted(base | set(list(useful_jd_words)[:20]))


def analyze_resume(resume_text, job_description, target_role):
    client = GeminiClient()
    ai_result = client.generate_json(ats_prompt(resume_text, job_description))
    if ai_result:
        return {
            'score': int(ai_result.get('score', 0)),
            'matched_keywords': ai_result.get('matched_keywords', []),
            'missing_keywords': ai_result.get('missing_keywords', []),
            'skill_gaps': ai_result.get('skill_gaps', []),
            'formatting_issues': ai_result.get('formatting_issues', []),
            'improvement_suggestions': ai_result.get('improvement_suggestions', []),
            'detailed_report': ai_result.get('detailed_report', []),
        }

    resume_words = normalize_words(resume_text)
    keywords = expected_keywords(target_role, job_description)
    matched = [keyword for keyword in keywords if keyword.lower() in resume_words or keyword.lower() in (resume_text or '').lower()]
    missing = [keyword for keyword in keywords if keyword not in matched]
    score = round((len(matched) / max(len(keywords), 1)) * 100)

    formatting_issues = []
    if len(resume_text or '') < 500:
        formatting_issues.append('Resume text is short; add measurable project and experience details.')
    if '@' not in (resume_text or ''):
        formatting_issues.append('Add a professional email address in the header.')
    if not re.search(r'\b(project|experience|education|skills)\b', resume_text or '', re.I):
        formatting_issues.append('Use clear section headings such as Skills, Projects, Experience, and Education.')

    suggestions = [
        f'Add evidence for missing keyword: {keyword}.'
        for keyword in missing[:5]
    ] or ['Resume matches the role well; improve impact by adding metrics and outcomes.']
    detailed_report = build_detailed_report(resume_text, missing, formatting_issues)

    return {
        'score': min(100, max(0, score)),
        'matched_keywords': matched,
        'missing_keywords': missing[:12],
        'skill_gaps': missing[:6],
        'formatting_issues': formatting_issues,
        'improvement_suggestions': suggestions,
        'detailed_report': detailed_report,
    }


def build_detailed_report(resume_text, missing_keywords, formatting_issues):
    report = []
    for keyword in missing_keywords[:6]:
        report.append({
            'area': f'Missing keyword: {keyword}',
            'mistake': 'The resume does not clearly mention this role keyword.',
            'why_it_matters': 'ATS systems and recruiters scan for exact role language from the job description.',
            'what_to_change': f'Add {keyword} naturally in the Skills section or in a project bullet.',
            'example_fix': f'Built a project using {keyword} to solve a measurable user or business problem.',
        })

    for issue in formatting_issues:
        report.append({
            'area': 'Resume formatting',
            'mistake': issue,
            'why_it_matters': 'Clean structure helps ATS parsing and lets recruiters find proof quickly.',
            'what_to_change': 'Use simple headings, bullet points, contact info, and measurable impact statements.',
            'example_fix': 'Projects: AI Career Prep Platform - improved interview readiness with ATS scoring and feedback reports.',
        })

    if not re.search(r'\d+%|\d+\+|\$\d+|\b\d+ users?\b', resume_text or '', re.I):
        report.append({
            'area': 'Impact metrics',
            'mistake': 'Resume bullets do not show numbers or measurable outcomes.',
            'why_it_matters': 'Metrics make your work easier to trust and compare.',
            'what_to_change': 'Add numbers such as users, accuracy, latency, score improvement, time saved, or features shipped.',
            'example_fix': 'Reduced manual resume review time by 60% by building an automated ATS feedback workflow.',
        })

    return report[:10]
