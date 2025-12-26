#!/usr/bin/env python3
"""
Script to prepare migration files with environment variables substituted.
This allows using .env values in SQL migration files.

Usage:
    python scripts/prepare_migration_with_env.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env file
env_file = project_root / '.env'
if env_file.exists():
    load_dotenv(env_file)
else:
    print("⚠️  Warning: .env file not found. Using system environment variables.")

# Get environment variables
db_app_user_password = os.getenv('DB_APP_USER_PASSWORD', 'CHANGE_ME_IN_PRODUCTION')
db_app_readonly_password = os.getenv('DB_APP_READONLY_PASSWORD', 'CHANGE_ME_IN_PRODUCTION')
db_app_migrator_password = os.getenv('DB_APP_MIGRATOR_PASSWORD', 'CHANGE_ME_IN_PRODUCTION')

# Migration file to update
migration_file = project_root / 'db' / 'migration' / '0.0.40__roles_and_permissions.sql'

if not migration_file.exists():
    print(f"❌ Migration file not found: {migration_file}")
    sys.exit(1)

# Read the migration file
with open(migration_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace placeholders with environment variables
content = content.replace(
    "CREATE ROLE app_user WITH LOGIN PASSWORD 'CHANGE_ME_IN_PRODUCTION';",
    f"CREATE ROLE app_user WITH LOGIN PASSWORD '{db_app_user_password}';"
)
content = content.replace(
    "CREATE ROLE app_readonly WITH LOGIN PASSWORD 'CHANGE_ME_IN_PRODUCTION';",
    f"CREATE ROLE app_readonly WITH LOGIN PASSWORD '{db_app_readonly_password}';"
)
content = content.replace(
    "CREATE ROLE app_migrator WITH LOGIN PASSWORD 'CHANGE_ME_IN_PRODUCTION';",
    f"CREATE ROLE app_migrator WITH LOGIN PASSWORD '{db_app_migrator_password}';"
)

# Write back (or create a new file)
output_file = project_root / 'db' / 'migration' / '0.0.40__roles_and_permissions_prepared.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Created prepared migration file: {output_file}")
print("⚠️  Note: Review the file and use it instead of the original if you want to use .env passwords.")
print("⚠️  Or manually update 0.0.40__roles_and_permissions.sql with your passwords.")

