# High Level Design (HLD)

## AI Job Application Agent

---

# 1. Project Overview

## Project Name

AI Job Application Agent

## Purpose

The AI Job Application Agent automates the job application process for job seekers.

The system analyzes a candidate's resume, finds suitable jobs, calculates matching scores, generates customized resumes and cover letters, fills application forms automatically, and tracks all applications.

---

# 2. Problem Statement

Job seekers spend significant time on:

- Searching jobs manually
- Reading job descriptions
- Editing resumes for every application
- Writing cover letters repeatedly
- Filling application forms
- Tracking application status

These tasks are repetitive and time-consuming.

The AI Job Application Agent reduces manual effort and improves application efficiency.

---

# 3. System Objectives

The system should:

- Read and analyze resumes
- Extract candidate skills
- Search and analyze job descriptions
- Match jobs with candidate profiles
- Generate tailored resumes
- Generate cover letters
- Automate form filling
- Track application status
- Generate reports and insights

---

# 4. User Flow

```text
User
 │
 ▼
Upload Resume
 │
 ▼
Resume Analyzer Agent
 │
 ▼
Skill Extraction
 │
 ▼
Job Search Agent
 │
 ▼
Job Matching Agent
 │
 ▼
Resume Customizer Agent
 │
 ▼
Cover Letter Agent
 │
 ▼
Application Agent
 │
 ▼
Application Tracker
 │
 ▼
Database Storage
 │
 ▼
Dashboard & Reports
```

---

# 5. System Components

## 5.1 User Interface Layer

Responsibilities:

- Upload Resume
- Search Jobs
- View Job Matches
- View Reports
- Track Applications

Technology:

- FastAPI Swagger UI (Phase 1)
- React (Optional Future Upgrade)

---

## 5.2 FastAPI Backend

Responsibilities:

- API Handling
- Request Validation
- Agent Communication
- Database Operations
- Response Generation

Technology:

- FastAPI
- Pydantic

---

## 5.3 Resume Analyzer Agent

Responsibilities:

- Read Resume
- Extract Skills
- Extract Education
- Extract Experience
- Extract Projects
- Create Candidate Profile

Input:

```text
Resume PDF
```

Output:

```json
{
  "name": "John",
  "skills": ["Python", "FastAPI"],
  "experience": "2 Years"
}
```

---

## 5.4 Job Search Agent

Responsibilities:

- Search Job Listings
- Collect Job Descriptions
- Filter Jobs

Input:

```text
Candidate Skills
```

Output:

```text
Relevant Job Listings
```

---

## 5.5 Job Matching Agent

Responsibilities:

- Compare Resume and Job Description
- Calculate Match Score
- Rank Jobs

Example:

```text
Resume Score: 87%
```

---

## 5.6 Resume Customizer Agent

Responsibilities:

- Tailor Resume
- Highlight Relevant Skills
- Optimize Resume Content

Output:

```text
Customized Resume
```

---

## 5.7 Cover Letter Agent

Responsibilities:

- Generate Personalized Cover Letter
- Align with Job Description
- Improve Application Quality

Output:

```text
Cover Letter
```

---

## 5.8 Browser Automation Agent

Responsibilities:

- Open Career Website
- Fill Forms
- Upload Resume
- Submit Applications

Technology:

- Playwright

---

## 5.9 Application Tracker

Responsibilities:

- Store Application Records
- Track Status
- Generate Statistics

Status Examples:

```text
Applied
Interview Scheduled
Rejected
Offer Received
```

---

# 6. High-Level Architecture

```text
                     ┌─────────────────┐
                     │      User       │
                     └────────┬────────┘
                              │
                              ▼
                  ┌─────────────────────┐
                  │      FastAPI        │
                  │    Backend APIs     │
                  └────────┬────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Resume      │    │ Job         │    │ Cover       │
│ Analyzer    │    │ Matching    │    │ Letter      │
│ Agent       │    │ Agent       │    │ Agent       │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────┬───────┴──────────┬───────┘
                  │                  │
                  ▼                  ▼

           ┌─────────────┐    ┌─────────────┐
           │   MySQL     │    │  ChromaDB   │
           │ Database    │    │ Vector DB   │
           └─────────────┘    └─────────────┘
```

---

# 7. Database Modules

## Users

Stores user information.

Fields:

```text
user_id
name
email
created_at
```

---

## Resumes

Stores uploaded resumes.

Fields:

```text
resume_id
user_id
file_path
uploaded_at
```

---

## Jobs

Stores job details.

Fields:

```text
job_id
company_name
job_title
job_description
location
```

---

## Applications

Stores job application records.

Fields:

```text
application_id
user_id
job_id
status
applied_date
```

---

## Agent Logs

Stores AI agent execution logs.

Fields:

```text
log_id
agent_name
action
timestamp
```

---

# 8. External Integrations

## OpenAI API

Used for:

- Resume Analysis
- Job Matching
- Cover Letter Generation
- Resume Customization

---

## Playwright

Used for:

- Browser Automation
- Form Filling
- Resume Upload
- Application Submission

---

## MySQL

Used for:

- Persistent Storage
- Application Tracking
- User Data

---

## ChromaDB

Used for:

- Resume Embeddings
- Job Description Embeddings
- Semantic Search
- RAG Implementation

---

# 9. Future Enhancements

- LinkedIn Integration
- Email Notifications
- Multi-Agent Collaboration
- Interview Preparation Agent
- Analytics Dashboard
- Multi-User Authentication

---

# HLD Approval Criteria

The system is considered correctly designed if it can:

- Analyze resumes
- Match jobs accurately
- Generate tailored documents
- Automate applications
- Track job application lifecycle
- Scale with modular architecture

---
