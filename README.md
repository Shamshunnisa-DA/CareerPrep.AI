# CareerPrep.AI
This is an application for getting your ats score checked and giving ai mock interview for pre and a detailed study plan for ur interview

# AI Career Prep Platform

Django web app and API for a career-preparation product with:

- ATS resume analysis
- AI/mock interview sessions
- Personalized study plan generation

The app works without an AI key using deterministic local scoring. Add `GEMINI_API_KEY`
to enable Gemini JSON responses.

## Run

```powershell
cd careerprep
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the dashboard.

## API

Health check:

```http
GET /api/health/
```

ATS analysis:

```http
POST /api/ats/analyze/
Content-Type: multipart/form-data

target_role=python
job_description=...
resume_text=...
resume=<optional file>
```

Start interview:

```http
POST /api/interview/start/
Content-Type: application/json

{"role":"python","difficulty":"medium","question_count":5}
```

Submit interview:

```http
POST /api/interview/sessions/{id}/submit/
Content-Type: application/json

{"answers":[{"question_id":1,"answer":"..."}]}
```

Generate study plan:

```http
POST /api/study-plan/generate/
Content-Type: application/json

{"target_role":"python","ats_analysis_id":1,"interview_session_id":1,"days":7}
```
