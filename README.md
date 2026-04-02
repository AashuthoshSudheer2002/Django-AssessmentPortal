📌 TestProject – Django Evaluation System
📖 Project Overview

Project overview
testproject is a Django 5.2 web application for managing an evaluation workflow with: 

candidate registration
roles and sections
criteria definition
evaluator assignment
candidate-criterion scoring
admin/out-of-box management
Root project folder: testproject
Django app: assessment_app

Quick start
Activate virtualenv:
Windows:
tenv\Scripts\activate
Linux/macOS:
source tenv/bin/activate
Install requirements:
pip install -r requirements.txt
Apply migrations:
python manage.py migrate
Create superuser:
python manage.py createsuperuser
Run server:
python manage.py runserver
Open:
http://127.0.0.1:8000/
admin at http://127.0.0.1:8000/admin/
Project structure
manage.py (Django management CLI)
settings.py (settings)
urls.py (global URL routes)
assessment_app (main app)
models.py (app models)
forms.py (forms)
views.py (view logic)
urls.py (app routes)
admin.py (admin registration)
templates/ (templates)
migrations/ (db migrations)
Core model entities
Based on migrations (with field details in migrations):

Role
title (unique)
Section
title (unique)
Candidate
name
email
resume (FileField upload_to='resumes/', nullable/blankable)
role (FK to Role, related_name probably candidaterole)
Evaluator
candidate (FK -> Candidate)
user (FK -> settings.AUTH_USER_MODEL)
section (FK -> Section, related_name evalsect)
unique_together ('user', 'candidate')
Criteria
criteria_title (CharField max=100, unique)
criteria_description (TextField)
criteria_weight (IntegerField validator >=0)
criteria_score (IntegerField null, blank, validators 0..10)
criteria_section (FK -> Section, related_name criteria)
CandidateCriterionScore
score (IntegerField validators 0..10)
candidate (FK -> Candidate)
criterion (FK -> Criteria)
evaluator (FK -> Evaluator)
unique/etc modifications through migrations 0005..0016 to enforce constraints (e.g., unique_together, is_evaluated)
Key app files
models.py
forms.py
views.py
urls.py
admin.py
testproject/assessment_app/templates/:
home.html
candidate/*.html
criteria/*.html
Evaluator/*.html
section/*.html
plus shared templates: candidatescores.html, login.html, partial_section_evaluator_form.html, etc.
URL routing
In urls.py:

admin/ -> Django admin
'' -> includes assessment_app.urls
'' -> views.home (likely home page)
In urls.py (expected patterns):

candidate endpoints (list/detail/register/score)
criteria endpoints (register, submit score, etc)
evaluator workflow endpoints
likely used by JS static/js/evaluator_dynamic.js
Forms and input
assessment_app/forms.py likely has:

Candidate registration form
Criteria form
Evaluator assignment/form
Scoring forms (criteria and candidate criteria score)
Admin
assessment_app/admin.py registers models for Django admin:

Role
Section
Candidate
Evaluator
Criteria
CandidateCriterionScore
Usage (common commands)
Run migrations:
python manage.py makemigrations
python manage.py migrate
Run tests:
python manage.py test
Create data via admin:
python manage.py shell or admin interface.
Collect static (if required for deployment):
python manage.py collectstatic
Sample data flow
Admin creates Roles, Sections, Criteria.
Candidates are created/registered with role+resume.
Evaluators assigned to candidates/sections.
Evaluators submit scores per candidate and criterion via CandidateCriterionScore.
App aggregates or displays totals in templates e.g. candidatescores.html, criteria/submitscore.html.
Special project points
SQLite DB in db.sqlite3
file uploads to media/resumes/
static JS in static/js/evaluator_dynamic.js for dynamic evaluator form behavior (partial form includes in template)
uses Django built-in auth and admin
Notes
STATIC_ROOT, MEDIA_ROOT, STATICFILES_DIRS, MEDIA_URL, STATIC_URL configured in settings.py.
could be production ported by adjusting DEBUG and allowed hosts.
