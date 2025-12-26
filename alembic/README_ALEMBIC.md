# Alembic Setup Guide

This project uses Alembic for database migration management. Alembic is configured to execute the existing SQL migration files in `db/migration/`.

## Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** running locally
3. **Virtual environment** (recommended)

## Setup Instructions

### 1. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install alembic sqlalchemy psycopg2-binary python-dotenv
```

### 3. Configure Database Connection

**DATABASE_URL is required and must be set in `.env` file or as an environment variable.**

Create a `.env` file in the project root:

```bash
cp env.example .env
```

Edit `.env` and set your database URL (this is required):

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/quiz_api
```

**Note:** The `alembic.ini` file no longer contains a hardcoded database URL. 
You must set `DATABASE_URL` in your `.env` file or as a system environment variable.

### 4. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE quiz_api;

# Exit psql
\q
```

### 5. Run Migrations

```bash
# Check current migration status
alembic current

# Show migration history
alembic history

# Run all pending migrations
alembic upgrade head

# Run migrations up to a specific revision
alembic upgrade 0020

# Rollback one migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade 0010
```

## Migration Files

The Alembic revisions are located in `alembic/versions/` and reference the SQL files in `db/migration/`:

- `0010_initial_schema.py` → `db/migration/0.0.10__initial_schema.sql`
- `0020_indexes_and_constraints.py` → `db/migration/0.0.20__indexes_and_constraints.sql`
- `0030_rls_policies.py` → `db/migration/0.0.30__rls_policies.sql`
- `0040_roles_and_permissions.py` → `db/migration/0.0.40__roles_and_permissions.sql`

## Creating New Migrations

### Option 1: Create Empty Revision (for raw SQL)

```bash
alembic revision -m "add_new_feature"
```

Then edit the generated file in `alembic/versions/` to execute your SQL file.

### Option 2: Auto-generate from Models (if using SQLAlchemy models)

```bash
alembic revision --autogenerate -m "add_new_table"
```

## Common Commands

```bash
# Show current database version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads

# Upgrade to latest
alembic upgrade head

# Downgrade one step
alembic downgrade -1

# Show SQL that would be executed (without running)
alembic upgrade head --sql
```

## Troubleshooting

### Connection Issues

If you get connection errors:

1. Verify PostgreSQL is running:
   ```bash
   pg_isready
   ```

2. Check database exists:
   ```bash
   psql -U postgres -l | grep quiz_api
   ```

3. Verify DATABASE_URL is correct:
   ```bash
   echo $DATABASE_URL
   ```

### Migration Already Applied

If you see "Target database is not up to date":

```bash
# Check current version
alembic current

# If needed, stamp the database with current version
alembic stamp head
```

### Permission Errors

If you get permission errors:

1. Ensure database user has proper permissions
2. Check PostgreSQL `pg_hba.conf` allows local connections
3. Verify user can create tables and extensions

## Project Structure

```
tutor-api/
├── alembic/
│   ├── versions/
│   │   ├── 0010_initial_schema.py
│   │   ├── 0020_indexes_and_constraints.py
│   │   ├── 0030_rls_policies.py
│   │   └── 0040_roles_and_permissions.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── db/
│   └── migration/
│       ├── 0.0.10__initial_schema.sql
│       ├── 0.0.20__indexes_and_constraints.sql
│       ├── 0.0.30__rls_policies.sql
│       └── 0.0.40__roles_and_permissions.sql
├── requirements.txt
└── .env (create this from .env.example)
```

## Next Steps

1. Set up your local database
2. Configure `.env` with your database credentials
3. Run `alembic upgrade head` to apply all migrations
4. Verify the database schema was created correctly

## Notes

- The Alembic revisions execute the existing SQL files, so you don't need to rewrite your migrations
- Downgrade functions are not implemented (would require separate rollback SQL files)
- For production, use environment variables for database credentials
- Consider using Secret Manager or similar for production deployments

