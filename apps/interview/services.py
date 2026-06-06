from apps.common.constants import DIFFICULTY_LEVELS, ROLE_SKILLS
from core.ai.gemini_client import GeminiClient
from core.ai.prompts import interview_feedback_prompt, interview_question_prompt


QUESTION_BANK = {
    'easy': [
        'Explain the most important concepts in {skill}.',
        'What problem did you solve using {skill} in a project?',
        'How would you describe {skill} to a beginner?',
    ],
    'medium': [
        'Design a small feature using {skill} and explain your tradeoffs.',
        'How do you debug production issues related to {skill}?',
        'What are common mistakes developers make with {skill}?',
    ],
    'hard': [
        'How would you scale a system that depends heavily on {skill}?',
        'Compare two advanced approaches in {skill} and defend your choice.',
        'Walk through a failure scenario involving {skill} and how you would recover.',
    ],
}


def role_skills(role):
    return ROLE_SKILLS.get((role or '').strip().lower(), ROLE_SKILLS['backend'])


def generate_questions(role, difficulty='medium', question_count=5):
    difficulty = difficulty if difficulty in DIFFICULTY_LEVELS else 'medium'
    question_count = min(max(int(question_count or 5), 1), 10)

    client = GeminiClient()
    ai_result = client.generate_json(interview_question_prompt(role, difficulty, question_count))
    if ai_result and ai_result.get('questions'):
        normalized = []
        for index, question in enumerate(ai_result['questions'][:question_count]):
            normalized.append({
                'id': index + 1,
                'question': question.get('question', ''),
                'topic': question.get('topic', role),
                'expected_points': question.get('expected_points', []),
            })
        return normalized

    skills = role_skills(role)
    templates = QUESTION_BANK[difficulty]
    questions = []
    for index in range(question_count):
        skill = skills[index % len(skills)]
        template = templates[index % len(templates)]
        questions.append({
            'id': index + 1,
            'question': template.format(skill=skill),
            'topic': skill,
            'expected_points': [
                f'Clear explanation of {skill}',
                'Relevant example from a project or scenario',
                'Tradeoffs, edge cases, or best practices',
            ],
        })
    return questions


def evaluate_answers(role, questions, answers):
    client = GeminiClient()
    ai_result = client.generate_json(interview_feedback_prompt(role, answers))
    if ai_result:
        return {
            'score': int(ai_result.get('score', 0)),
            'feedback': {
                'communication_score': ai_result.get('communication_score', 0),
                'correctness_score': ai_result.get('correctness_score', 0),
                'confidence_score': ai_result.get('confidence_score', 0),
                'strengths': ai_result.get('strengths', []),
                'improvements': ai_result.get('improvements', []),
                'next_practice_topics': ai_result.get('next_practice_topics', []),
                'detailed_report': ai_result.get('detailed_report', []),
                'video_tips': ai_result.get('video_tips', []),
            },
        }

    answer_map = {
        int(item.get('question_id', index + 1)): item.get('answer', '')
        for index, item in enumerate(answers or [])
    }
    per_question = []
    total = 0
    for question in questions:
        question_id = int(question.get('id', len(per_question) + 1))
        answer = answer_map.get(question_id, '')
        expected = question.get('expected_points', [])
        score = 25
        if len(answer.split()) >= 25:
            score += 25
        if any(point.split()[0].lower() in answer.lower() for point in expected):
            score += 25
        if any(word in answer.lower() for word in ['example', 'project', 'tradeoff', 'because', 'tested']):
            score += 25
        missing_points = [
            point for point in expected
            if point.split()[0].lower() not in answer.lower()
        ]
        total += score
        per_question.append({
            'question_id': question_id,
            'question': question.get('question', ''),
            'topic': question.get('topic'),
            'score': score,
            'comment': 'Good structure; add more concrete metrics or examples.' if score >= 70 else 'Answer needs more detail, examples, and technical accuracy.',
            'mistake': build_answer_mistake(answer, missing_points),
            'why_it_matters': 'Interviewers score answers on clarity, correctness, evidence, and decision-making.',
            'what_to_change': 'Use STAR: Situation, Task, Action, Result. Add one project example and one measurable outcome.',
            'example_answer': build_example_answer(question),
        })

    average = round(total / max(len(questions), 1))
    return {
        'score': average,
        'feedback': {
            'communication_score': min(100, average + 5),
            'correctness_score': average,
            'confidence_score': max(0, average - 5),
            'strengths': ['Shows role awareness', 'Attempts to connect answers to practical work'],
            'improvements': ['Use the STAR format', 'Mention tools, constraints, and measurable outcomes'],
            'next_practice_topics': [question.get('topic') for question in questions[:3]],
            'per_question': per_question,
            'detailed_report': build_interview_report(per_question),
            'video_tips': [
                'Keep your face centered and camera at eye level.',
                'Answer in 60-90 seconds, then pause instead of rambling.',
                'Speak slightly slower than normal and look at the camera for key points.',
                'Use a quiet background and check lighting before starting.',
            ],
        },
    }


def build_answer_mistake(answer, missing_points):
    if not answer.strip():
        return 'No answer was submitted for this question.'
    if len(answer.split()) < 25:
        return 'The answer is too short to prove depth.'
    if missing_points:
        return f'Missing expected point: {missing_points[0]}.'
    return 'The answer is acceptable but can be stronger with metrics and tradeoffs.'


def build_example_answer(question):
    topic = question.get('topic') or 'the topic'
    return (
        f'In my project, I used {topic} to solve a specific problem. '
        f'My task was to design the feature, handle edge cases, and test it. '
        f'I chose this approach because it improved reliability and made the code easier to maintain. '
        f'The result was a working feature with clearer performance or user impact.'
    )


def build_interview_report(per_question):
    return [
        {
            'area': f"Question {item['question_id']}: {item.get('topic') or 'general'}",
            'mistake': item['mistake'],
            'why_it_matters': item['why_it_matters'],
            'what_to_change': item['what_to_change'],
            'example_fix': item['example_answer'],
        }
        for item in per_question
    ]
