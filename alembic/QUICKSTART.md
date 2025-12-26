# Quick Start Guide - Alembic Setup

## Prerequisites

- Python 3.11+
- PostgreSQL installed and running
- Database `quiz_api` created (or create it)

## Quick Setup (5 minutes)

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Create `.env` file from template:

```bash
cp env.example .env
```

Edit `.env` and update the `DATABASE_URL` with your actual credentials:

```bash
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/quiz_api
```

**IMPORTANT:** `DATABASE_URL` is required. Alembic will fail if it's not set.

### 4. Create Database

```bash
# Option 1: Using createdb
createdb quiz_api

# Option 2: Using psql
psql -U postgres
CREATE DATABASE quiz_api;
\q
```

### 5. Run Migrations

```bash
# Check status
alembic current

# Run all migrations
alembic upgrade head

# Verify
alembic current
```

## Verify Setup

```bash
# Check Alembic can connect
alembic current

# Should show: (empty) if no migrations run yet
# Or show revision number if migrations have run

# Check database has tables
psql -U postgres -d quiz_api -c "\dt"
```

## Common Commands

```bash
# Show migration history
alembic history

# Show current version
alembic current

# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade 0020

# Downgrade one step
alembic downgrade -1

# Show SQL without executing
alembic upgrade head --sql
```

## Troubleshooting

### "Can't connect to database"

1. Check PostgreSQL is running: `pg_isready`
2. Verify DATABASE_URL in `.env` is correct
3. Test connection: `psql $DATABASE_URL`

### "No such file or directory" (SQL files)

Make sure you're running from the project root directory.

### "Module not found: alembic"

Activate your virtual environment: `source venv/bin/activate`

## Next Steps

Once migrations are applied, you can:
- Start developing your API
- Create new migrations as needed
- Use Alembic to manage schema changes

For detailed information, see `README_ALEMBIC.md`.

