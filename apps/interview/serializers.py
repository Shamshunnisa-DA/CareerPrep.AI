def serialize_interview_session(session):
    return {
        'id': session.id,
        'role': session.role,
        'difficulty': session.difficulty,
        'question_count': session.question_count,
        'questions': session.questions,
        'answers': session.answers,
        'score': session.score,
        'feedback': session.feedback,
        'created_at': session.created_at.isoformat(),
        'updated_at': session.updated_at.isoformat(),
    }
