# Quiz API Source Code

This directory contains the FastAPI application source code generated from the OpenAPI specification.

## Project Structure

```
src/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── core/                   # Core application modules
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database setup and session management
│   ├── security.py        # Security utilities (JWT, password hashing)
│   ├── exceptions.py      # Custom exceptions
│   └── dependencies.py    # FastAPI dependencies
├── models/                # Database models (SQLAlchemy)
│   ├── __init__.py
│   ├── user.py           # User-related enums
│   └── database.py       # SQLAlchemy models
├── schemas/               # Pydantic schemas
│   ├── __init__.py
│   ├── auth.py           # Authentication schemas
│   └── common.py         # Common schemas
├── api/                   # API routes
│   └── v1/
│       ├── __init__.py
│       ├── router.py     # Main API router
│       └── endpoints/    # Endpoint modules
│           ├── auth.py
│           ├── questions.py
│           ├── answers.py
│           ├── hints.py
│           ├── sessions.py
│           ├── progress.py
│           ├── students.py
│           ├── tutors.py
│           ├── messages.py
│           ├── subjects.py
│           ├── competitions.py
│           ├── tenants.py
│           ├── system_admin.py
│           └── tenant_admin.py
└── services/              # Business logic layer
    ├── __init__.py
    ├── auth.py           # Authentication service
    └── tenant.py          # Tenant service
```

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `env.example` to `.env` and configure:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/quiz_api
JWT_SECRET_KEY=your-secret-key-here
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Run the Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000/api/v1
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Implementation Status

### ✅ Completed
- Project structure
- Core configuration and database setup
- Authentication endpoints (login, logout, password management)
- Database models (basic structure)
- Security utilities (JWT, password hashing)
- Tenant resolution service

### 🚧 TODO (Placeholder endpoints created)
- Question generation and retrieval
- Answer submission and validation
- Hint generation
- Session management
- Progress tracking
- Student/Tutor management
- Messaging system
- Subject management
- Competition management
- System/Tenant admin endpoints

## Development Notes

1. **Database Models**: The models in `src/models/database.py` are basic implementations. You may need to add more relationships and fields based on your requirements.

2. **Services**: Business logic should be implemented in the `services/` directory. The authentication service is partially implemented as an example.

3. **Endpoints**: Most endpoints are placeholder stubs. Implement the business logic in the corresponding service classes and call them from the endpoints.

4. **Authentication**: JWT-based authentication is implemented. The `get_current_user` dependency needs to be properly integrated with the database models.

5. **Multi-tenancy**: Tenant resolution is implemented. Make sure to set tenant context in database sessions for RLS to work properly.

6. **Error Handling**: Custom exceptions are defined. Use them consistently throughout the application.

## Next Steps

1. Implement remaining service classes
2. Complete endpoint implementations
3. Add AI integration for question generation
4. Implement email service for OTP and notifications
5. Add comprehensive error handling
6. Add request validation
7. Implement rate limiting
8. Add logging and monitoring
9. Write unit and integration tests
10. Add API documentation

