#!/usr/bin/env python3
"""
Generate SQL INSERT statement for system admin account from environment variables.

This script reads admin account details from environment variables and generates
a SQL INSERT statement that can be manually executed in the database.

Environment variables required:
    SYSTEM_ADMIN_USERNAME - Username for the system admin
    SYSTEM_ADMIN_EMAIL - Email address for the system admin
    SYSTEM_ADMIN_NAME - Full name of the system admin
    SYSTEM_ADMIN_PASSWORD - Temporary password (will be hashed)

Usage:
    python scripts/create_system_admin_from_env.py

Or set variables inline:
    SYSTEM_ADMIN_USERNAME=admin SYSTEM_ADMIN_EMAIL=admin@example.com python scripts/create_system_admin_from_env.py

The generated SQL can be run manually, for example:
    psql -d your_database -c "$(python scripts/create_system_admin_from_env.py)"
"""
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime

# Try to use bcrypt directly first (more reliable)
try:
    import bcrypt
    USE_BCRYPT_DIRECT = True
except ImportError:
    USE_BCRYPT_DIRECT = False
    # Fallback to passlib if bcrypt not available
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    except ImportError:
        print("Error: Neither bcrypt nor passlib is available.")
        print("Please install: pip install bcrypt")
        sys.exit(1)

# Load .env file (with error handling)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, verbose=False)  # verbose=False to suppress parsing warnings
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    print("Continuing with environment variables from system...")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# No database imports needed - we're just generating SQL


def get_password_hash_safe(password: str) -> str:
    """
    Generate password hash using bcrypt directly (more reliable than passlib).
    Falls back to passlib if bcrypt is not available.
    """
    # Ensure password is bytes (bcrypt requirement)
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    # Truncate password if longer than 72 bytes (bcrypt limit)
    if len(password_bytes) > 72:
        print(f"Warning: Password is longer than 72 bytes, truncating...")
        password_bytes = password_bytes[:72]
    
    # Generate bcrypt hash
    if USE_BCRYPT_DIRECT:
        # Use bcrypt directly (more reliable)
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    else:
        # Fallback to passlib
        password_hash = pwd_context.hash(password)
    
    return password_hash


def create_system_admin_from_env():
    """Create system admin account from environment variables"""
    # Get values from environment
    username = os.getenv("SYSTEM_ADMIN_USERNAME")
    email = os.getenv("SYSTEM_ADMIN_EMAIL")
    name = os.getenv("SYSTEM_ADMIN_NAME", "System Administrator")
    password = os.getenv("SYSTEM_ADMIN_PASSWORD")
    
    # Validate required variables
    if not username:
        print("Error: SYSTEM_ADMIN_USERNAME environment variable is required")
        print("Add it to your .env file or set it as an environment variable")
        sys.exit(1)
    
    if not email:
        print("Error: SYSTEM_ADMIN_EMAIL environment variable is required")
        print("Add it to your .env file or set it as an environment variable")
        sys.exit(1)
    
    if not password:
        print("Error: SYSTEM_ADMIN_PASSWORD environment variable is required")
        print("Set a temporary password that will be changed on first login")
        print("Add it to your .env file or set it as an environment variable")
        sys.exit(1)
    
    # Generate password hash
    print("Generating password hash...", file=sys.stderr)
    password_hash = get_password_hash_safe(password)
    
    # Generate UUID for admin_id
    admin_id = str(uuid.uuid4())
    
    # Get current timestamp
    now = datetime.utcnow().isoformat()
    
    # Escape single quotes in SQL strings
    def escape_sql_string(s):
        if s is None:
            return 'NULL'
        return "'" + str(s).replace("'", "''") + "'"
    
    # Generate SQL INSERT statement with ON CONFLICT handling
    # Note: The table has constraints on username and email, so we handle conflicts on both
    sql = f"""-- System Admin Account INSERT Statement
-- Generated on: {now}
-- Username: {username}
-- Email: {email}
-- Name: {name}
-- 
-- IMPORTANT: This password hash is for the temporary password.
-- The user MUST change their password on first login!
-- Temporary Password: {password}
--
-- To run this SQL:
--   1. Connect as a user with app_migrator role, OR
--   2. Connect as postgres/superuser and run:
--      SET ROLE app_migrator;
--      [paste SQL below]
--   3. Or temporarily disable RLS:
--      SET LOCAL row_security = off;
--      [paste SQL below]

-- Handle conflicts on both username and email
DO $$
DECLARE
    existing_admin_id UUID;
    existing_username VARCHAR;
    existing_email VARCHAR;
BEGIN
    -- Check for existing account by username
    SELECT admin_id, username, email INTO existing_admin_id, existing_username, existing_email
    FROM administrator_accounts
    WHERE username = {escape_sql_string(username)}
    LIMIT 1;
    
    -- If found by username, update it
    IF existing_admin_id IS NOT NULL THEN
        -- Verify it's a system_admin before updating
        IF EXISTS (SELECT 1 FROM administrator_accounts WHERE admin_id = existing_admin_id AND role = 'system_admin'::user_role) THEN
            UPDATE administrator_accounts
            SET
                email = {escape_sql_string(email)},
                password_hash = {escape_sql_string(password_hash)},
                name = {escape_sql_string(name)},
                role = 'system_admin'::user_role,
                status = 'pending_activation'::account_status,
                requires_password_change = TRUE,
                tenant_id = NULL,
                updated_at = NOW()
            WHERE admin_id = existing_admin_id;
            RAISE NOTICE 'Updated existing system admin account with username: %', {escape_sql_string(username)};
        ELSE
            RAISE EXCEPTION 'Account with username % exists but is not a system_admin', {escape_sql_string(username)};
        END IF;
    ELSE
        -- Check for existing account by email
        SELECT admin_id, username, email INTO existing_admin_id, existing_username, existing_email
        FROM administrator_accounts
        WHERE email = {escape_sql_string(email)}
        LIMIT 1;
        
        -- If found by email, update it
        IF existing_admin_id IS NOT NULL THEN
            -- Verify it's a system_admin before updating
            IF EXISTS (SELECT 1 FROM administrator_accounts WHERE admin_id = existing_admin_id AND role = 'system_admin'::user_role) THEN
                UPDATE administrator_accounts
                SET
                    username = {escape_sql_string(username)},
                    password_hash = {escape_sql_string(password_hash)},
                    name = {escape_sql_string(name)},
                    role = 'system_admin'::user_role,
                    status = 'pending_activation'::account_status,
                    requires_password_change = TRUE,
                    tenant_id = NULL,
                    updated_at = NOW()
                WHERE admin_id = existing_admin_id;
                RAISE NOTICE 'Updated existing system admin account with email: %', {escape_sql_string(email)};
            ELSE
                RAISE EXCEPTION 'Account with email % exists but is not a system_admin', {escape_sql_string(email)};
            END IF;
        ELSE
            -- Insert new account
            INSERT INTO administrator_accounts (
                admin_id,
                tenant_id,
                username,
                email,
                password_hash,
                name,
                role,
                status,
                requires_password_change,
                created_at,
                updated_at
            ) VALUES (
                {escape_sql_string(admin_id)}::uuid,
                NULL,
                {escape_sql_string(username)},
                {escape_sql_string(email)},
                {escape_sql_string(password_hash)},
                {escape_sql_string(name)},
                'system_admin'::user_role,
                'pending_activation'::account_status,
                TRUE,
                NOW(),
                NOW()
            );
            RAISE NOTICE 'Created new system admin account: %', {escape_sql_string(username)};
        END IF;
    END IF;
END $$;
"""
    
    # Print SQL to stdout (so it can be piped to psql)
    print(sql)
    
    # Print summary to stderr (so it doesn't interfere with piping)
    print("\n" + "=" * 60, file=sys.stderr)
    print("SQL INSERT Statement Generated!", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Admin ID: {admin_id}", file=sys.stderr)
    print(f"Username: {username}", file=sys.stderr)
    print(f"Email: {email}", file=sys.stderr)
    print(f"Name: {name}", file=sys.stderr)
    print(f"Role: system_admin", file=sys.stderr)
    print(f"Status: pending_activation", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Temporary Password: {password}", file=sys.stderr)
    print("IMPORTANT: Change password on first login!", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("\nTo execute this SQL:", file=sys.stderr)
    print("  psql -d your_database -c \"$(python scripts/create_system_admin_from_env.py)\"", file=sys.stderr)
    print("Or copy the SQL above and run it manually in psql.", file=sys.stderr)


if __name__ == "__main__":
    create_system_admin_from_env()

