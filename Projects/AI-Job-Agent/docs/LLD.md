Low Level Design (LLD)
AI Job Application Agent

Create this file:

AI-Job-Agent/docs/LLD.md

1. What is LLD?
   High Level Design (HLD)

Tells us:

What modules exist?
How they communicate?
Low Level Design (LLD)

Tells us:

Which files exist?
Which classes exist?
Which functions exist?
Which APIs exist?
Which tables exist?

LLD is the blueprint developers use while coding.

2. Final Project Folder Structure
   AI-Job-Agent/
   │
   ├── docs/
   │ ├── SRS.md
   │ ├── HLD.md
   │ └── LLD.md
   │
   ├── backend/
   │
   │ ├── app/
   │ │
   │ ├── api/
   │ │ ├── resume_routes.py
   │ │ ├── job_routes.py
   │ │ ├── application_routes.py
   │ │ └── report_routes.py
   │ │
   │ ├── agents/
   │ │ ├── resume_agent.py
   │ │ ├── matching_agent.py
   │ │ ├── resume_customizer_agent.py
   │ │ ├── cover_letter_agent.py
   │ │ └── application_agent.py
   │ │
   │ ├── services/
   │ │ ├── pdf_service.py
   │ │ ├── embedding_service.py
   │ │ ├── llm_service.py
   │ │ └── job_service.py
   │ │
   │ ├── database/
   │ │ ├── db.py
   │ │ └── models/
   │ │
   │ ├── schemas/
   │ │ ├── resume_schema.py
   │ │ ├── job_schema.py
   │ │ └── application_schema.py
   │ │
   │ ├── core/
   │ │ ├── config.py
   │ │ └── constants.py
   │ │
   │ ├── utils/
   │ │ ├── logger.py
   │ │ └── helpers.py
   │ │
   │ └── main.py
   │
   ├── database/
   │ └── mysql_scripts/
   │
   ├── tests/
   │
   ├── .env
   ├── requirements.txt
   ├── docker-compose.yml
   └── README.md
3. Module Responsibilities
   api/

Contains FastAPI endpoints.

Example:

POST /resume/upload
POST /jobs/search
POST /applications/create
GET /reports
agents/

Contains AI logic.

Each agent performs a specific task.

resume_agent.py

Responsibilities:

Read resume
Extract skills
Extract projects
Extract experience

Functions:

analyze_resume()
extract_skills()
extract_projects()
matching_agent.py

Responsibilities:

Compare resume and job
Calculate score

Functions:

match_job()
calculate_score()
resume_customizer_agent.py

Responsibilities:

Generate custom resume

Functions:

customize_resume()
cover_letter_agent.py

Responsibilities:

Generate cover letter

Functions:

generate_cover_letter()
application_agent.py

Responsibilities:

Browser automation
Submit application

Functions:

apply_job()
upload_resume()
fill_form() 4. Service Layer Design
pdf_service.py

Purpose:

Read PDF files
Extract text

Functions:

read_pdf()
extract_text()
llm_service.py

Purpose:

Single place for OpenAI calls.

Functions:

get_completion()
generate_json()
embedding_service.py

Purpose:

Create embeddings.

Functions:

create_embedding()
store_embedding()
search_embedding()
job_service.py

Purpose:

Job searching.

Functions:

search_jobs()
filter_jobs() 5. Database Design
users
user_id
name
email
created_at
resumes
resume_id
user_id
resume_path
uploaded_at
jobs
job_id
company_name
job_title
description
location
applications
application_id
user_id
job_id
status
applied_date
agent_logs
log_id
agent_name
action
timestamp 6. API Design
Resume Upload
POST /resume/upload

Request:

{
"resume_file":"resume.pdf"
}

Response:

{
"message":"Resume Uploaded"
}
Analyze Resume
POST /resume/analyze

Response:

{
"skills":["Python","FastAPI"]
}
Search Jobs
POST /jobs/search

Request:

{
"keyword":"AI Engineer"
}
Match Job
POST /jobs/match

Response:

{
"score":87
}
Generate Cover Letter
POST /cover-letter/generate
Apply Job
POST /application/apply
Reports
GET /reports 7. Agent Workflow Design
Resume Upload
│
▼
Resume Agent
│
▼
Skill Extraction
│
▼
Job Search
│
▼
Matching Agent
│
▼
Resume Customizer
│
▼
Cover Letter Agent
│
▼
Application Agent
│
▼
Database 8. Environment Variables

File:

.env

Contents:

OPENAI_API_KEY=

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=ai_job_agent 9. Logging Strategy

Every agent action should be logged.

Example:

Resume uploaded
Resume analyzed
Job matched
Cover letter generated
Application submitted

Purpose:

Debugging
Monitoring
Audit trail 10. MVP Scope (2 Weeks)

We will build only:

✅ Resume Upload

✅ Resume Analysis

✅ Job Matching

✅ Cover Letter Generation

✅ Application Tracking

✅ MySQL Integration

✅ FastAPI APIs

✅ Basic LangGraph Workflow

❌ No Authentication

❌ No LinkedIn Automation

❌ No Multi-user System

❌ No Complex Dashboard
