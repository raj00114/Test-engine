# JHTET Test Engine

A Django-based online test and mock-test engine being developed for
JHTET 2026 preparation.

The project is designed to support bilingual (English/Hindi) questions,
practice tests, scoring, answer review, syllabus-based question
organization, and future online-exam features.

## Current Features

- Django-based web application
- JHTET 2026 syllabus management
- Primary and Upper-primary mathematics syllabus
- Bilingual English/Hindi questions
- Question bank management through Django Admin
- Test creation through Django Admin
- Published/unpublished tests
- Test-taking interface
- Multiple-choice questions
- Automatic score calculation
- Answered and unanswered question count
- Percentage score
- Correct/incorrect answer review
- Correct answer display
- English and Hindi explanations
- Retry test functionality
- Django development environment

## Technology Stack

- Python 3.14.7
- Django 6.1.1
- SQLite
- HTML
- Django Templates
- Git / GitHub

## Project Structure

```text
Test-engine/
│
├── manage.py
├── requirements.txt
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── engine/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/
│       ├── base.html
│       ├── home.html
│       └── tests/
│           ├── list.html
│           └── take.html
│
└── syllabus/
    ├── models.py
    ├── views.py
    ├── admin.py
    ├── syllabus_data.json
    └── management/
        └── commands/
            └── import_syllabus.py
