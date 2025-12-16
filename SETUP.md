# Quick Setup Guide

## 1. Navigate to Project
```bash
cd c:\Users\91797\Desktop\pi\book_management
```

## 2. Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

## 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

## 4. Configure Environment
```powershell
# Copy template
copy .env.example .env

# Edit .env file with your settings:
# - DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/book_management
# - SECRET_KEY=your-secret-key-here (generate a strong random key)
```

## 5. Create PostgreSQL Database
```sql
-- Connect to PostgreSQL first
psql -U postgres

-- Create database
CREATE DATABASE book_management;
```

## 6. Run Migrations
```powershell
alembic upgrade head
```

## 7. Start the Application
```powershell
uvicorn app.main:app --reload
```

## 8. Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Quick Test
1. Open http://localhost:8000/docs
2. Try the `/api/v1/auth/register` endpoint
3. Then `/api/v1/auth/login` to get tokens
4. Use the "Authorize" button with your access token
5. Try creating a book via `/api/v1/books/`

## Common Commands

### Database Migrations
```powershell
# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

### Running Tests (when implemented)
```powershell
pytest
```

## Troubleshooting

### Database Connection Error
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Migration Errors
- Drop and recreate database if needed
- Check model imports in alembic/env.py
