📌 TestProject – Django Evaluation System
📖 Project Overview

testproject is a Django 5.2 web application for managing an evaluation workflow with:

Candidate registration
Roles and sections
Criteria definition
Evaluator assignment
Candidate-criterion scoring
Admin/out-of-box management

Root project folder: testproject
Django app: assessment_app

🚀 Quick Start
🔹 Activate Virtual Environment

Windows

tenv\Scripts\activate

Linux/macOS

source tenv/bin/activate
🔹 Install Requirements
pip install -r requirements.txt
🔹 Apply Migrations
python manage.py migrate
🔹 Create Superuser
python manage.py createsuperuser
🔹 Run Server
python manage.py runserver
🌐 Access the Application
App: http://127.0.0.1:8000/
Admin: http://127.0.0.1:8000/admin/
📁 Project Structure
manage.py                # Django management CLI
settings.py              # Project settings
urls.py                  # Global URL routes

assessment_app/          # Main application
├── models.py            # App models
├── forms.py             # Forms
├── views.py             # View logic
├── urls.py              # App routes
├── admin.py             # Admin registration
├── migrations/          # Database migrations
└── templates/           # HTML templates
🧠 Core Model Entities
🔹 Role
title (unique)
🔹 Section
title (unique)
🔹 Candidate
name
email
resume (FileField → resumes/, nullable/blank)
role (ForeignKey → Role)
🔹 Evaluator
candidate (FK → Candidate)
user (FK → Django User model)
section (FK → Section)
Constraint: unique_together ('user', 'candidate')
🔹 Criteria
criteria_title (unique, max_length=100)
criteria_description
criteria_weight (Integer ≥ 0)
criteria_score (Integer 0–10, nullable)
criteria_section (FK → Section)
🔹 CandidateCriterionScore
score (Integer 0–10)
candidate (FK → Candidate)
criterion (FK → Criteria)
evaluator (FK → Evaluator)

Additional constraints enforced through migrations (0005–0016)

📂 Key App Files
models.py
forms.py
views.py
urls.py
admin.py
Templates
templates/
├── home.html
├── candidate/
├── criteria/
├── evaluator/
├── section/
├── candidatescores.html
├── login.html
└── partial_section_evaluator_form.html
🔗 URL Routing
Global (testproject/urls.py)
/admin/ → Django Admin
/ → Includes assessment_app.urls
/ → views.home
App Routing (assessment_app/urls.py)
Candidate endpoints (list, register, scoring)
Criteria endpoints
Evaluator workflows

Dynamic behavior handled via:

static/js/evaluator_dynamic.js
🧾 Forms & Input

Defined in assessment_app/forms.py:

Candidate Registration Form
Criteria Form
Evaluator Assignment Form
Scoring Forms
🛠️ Admin

Registered in assessment_app/admin.py:

Role
Section
Candidate
Evaluator
Criteria
CandidateCriterionScore
⚙️ Usage (Common Commands)
🔹 Migrations
python manage.py makemigrations
python manage.py migrate
🔹 Run Tests
python manage.py test
🔹 Django Shell
python manage.py shell
🔹 Collect Static Files
python manage.py collectstatic
🔄 Sample Data Flow
Admin creates:
Roles
Sections
Criteria
Candidates are registered with:
Role
Resume
Evaluators are assigned to:
Candidates
Sections
Evaluators submit scores via:
CandidateCriterionScore
Results displayed in:
candidatescores.html
criteria/submitscore.html
📦 Special Project Points
SQLite database (db.sqlite3)
File uploads → media/resumes/
Static JS → static/js/evaluator_dynamic.js
Uses Django built-in authentication & admin
⚠️ Notes
STATIC_ROOT, MEDIA_ROOT, STATICFILES_DIRS, MEDIA_URL, STATIC_URL configured in settings.py
For production:
Set DEBUG = False
Configure ALLOWED_HOSTS
📎 Reference Files
models.py
views.py
forms.py
urls.py
settings.py
db.sqlite3
