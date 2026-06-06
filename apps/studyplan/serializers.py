def serialize_study_plan(study_plan):
    return {
        'id': study_plan.id,
        'target_role': study_plan.target_role,
        'ats_score': study_plan.ats_score,
        'interview_score': study_plan.interview_score,
        'weak_topics': study_plan.weak_topics,
        'plan': study_plan.plan,
        'created_at': study_plan.created_at.isoformat(),
    }
