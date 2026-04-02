📌 TestProject – Django Evaluation System
📖 Project Overview

testproject is a Django 5.2 web application for managing an evaluation workflow with:

Candidate registration
Role and section management
Criteria definition
Evaluator assignment
Candidate-criterion scoring
Admin-based management
📁 Project Structure
testproject/
│
├── manage.py
├── db.sqlite3
├── testproject/
│   ├── settings.py
│   ├── urls.py
│
└── assessment_app/
    ├── models.py
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── migrations/
    └── templates/
        ├── home.html
        ├── candidate/
        ├── criteria/
        ├── evaluator/
        ├── section/
        ├── candidatescores.html
        ├── login.html
        └── partial_section_evaluator_form.html
🚀 Quick Start
1️⃣ Activate Virtual Environment

Windows:

tenv\Scripts\activate

Linux/macOS:

source tenv/bin/activate
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Apply Migrations
python manage.py migrate
4️⃣ Create Superuser
python manage.py createsuperuser
5️⃣ Run Server
python manage.py runserver
🌐 Access the App
App: http://127.0.0.1:8000/
Admin: http://127.0.0.1:8000/admin/
🧠 Core Model Entities
🔹 Role
title (unique)
🔹 Section
title (unique)
🔹 Candidate
name
email
resume (FileField → resumes/)
role (ForeignKey → Role)
🔹 Evaluator
candidate (FK → Candidate)
user (FK → Django User)
section (FK → Section)
Unique constraint: (user, candidate)
🔹 Criteria
criteria_title (unique)
criteria_description
criteria_weight
criteria_score
criteria_section (FK → Section)
🔹 CandidateCriterionScore
score
candidate (FK)
criterion (FK)
evaluator (FK)
🔗 URL Routing
Global (testproject/urls.py)
/admin/ → Django Admin
/ → Home + assessment_app.urls
App Routes (assessment_app/urls.py)
Candidate endpoints (register, list, score)
Criteria endpoints
Evaluator workflows

Dynamic JS interaction via:

static/js/evaluator_dynamic.js
🧾 Forms & Input

Defined in assessment_app/forms.py:

Candidate Registration Form
Criteria Form
Evaluator Assignment Form
Scoring Forms
🛠️ Admin Configuration

Registered in admin.py:

Role
Section
Candidate
Evaluator
Criteria
CandidateCriterionScore
⚙️ Common Commands
Create & Apply Migrations
python manage.py makemigrations
python manage.py migrate
Run Tests
python manage.py test
Django Shell
python manage.py shell
Collect Static Files
python manage.py collectstatic
🔄 Sample Workflow
Admin creates:
Roles
Sections
Criteria
Candidates are registered with:
Role
Resume
Evaluators are assigned:
To candidates
To sections
Evaluators submit scores:
Per candidate
Per criterion
Results displayed in:
candidatescores.html
criteria/submitscore.html
📂 Static & Media
Database: SQLite (db.sqlite3)
Media uploads: media/resumes/
Static files: static/
⚠️ Notes
Uses Django built-in authentication system
STATIC_ROOT, MEDIA_ROOT, etc. configured in settings.py
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
