def serialize_resume_analysis(analysis):
    return {
        'id': analysis.id,
        'candidate_name': analysis.candidate_name,
        'target_role': analysis.target_role,
        'score': analysis.score,
        'matched_keywords': analysis.matched_keywords,
        'missing_keywords': analysis.missing_keywords,
        'skill_gaps': analysis.skill_gaps,
        'formatting_issues': analysis.formatting_issues,
        'improvement_suggestions': analysis.improvement_suggestions,
        'detailed_report': analysis.detailed_report,
        'created_at': analysis.created_at.isoformat(),
    }
