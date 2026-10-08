# Secure Task Management API

FastAPI REST API with:

- JWT Authentication
- Password Hashing
- SQLite
- SQLAlchemy
- Pydantic
- CRUD Operations
- User-specific Tasks
- Task Filtering
- Task Completion

## Installation

Create virtual environment:

py -3.11 -m venv venv

Activate:

.\venv\Scripts\Activate.ps1

Install packages:

pip install -r requirements.txt

## Run

uvicorn main:app --reload

## Swagger

http://127.0.0.1:8000/docs

## APIs

POST /register

POST /login

GET /users/me

POST /tasks

GET /tasks

GET /tasks/{task_id}

PUT /tasks/{task_id}

DELETE /tasks/{task_id}

GET /my-tasks

PATCH /tasks/{task_id}/complete

## Authentication

Use:

Authorization: Bearer <access_token>

## Database

SQLite database:

task_management.db
