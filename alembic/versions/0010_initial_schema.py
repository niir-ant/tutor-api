"""initial_schema

Revision ID: 0010
Revises: 
Create Date: 2025-12-25 17:00:00.000000

"""
from alembic import op
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# revision identifiers, used by Alembic.
revision = '0010'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Execute initial schema migration from SQL file"""
    sql_file = project_root / 'db' / 'migration' / '0.0.10__initial_schema.sql'
    
    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Use connection to execute raw SQL
    # Split by semicolon and execute each statement separately
    # This handles comments and multi-line statements better
    connection = op.get_bind()
    
    # Split SQL into statements, handling comments and empty lines
    statements = []
    current_statement = []
    
    for line in sql.split('\n'):
        stripped = line.strip()
        # Skip empty lines and comment-only lines
        if not stripped or stripped.startswith('--'):
            continue
        current_statement.append(line)
        # If line ends with semicolon, it's the end of a statement
        if stripped.endswith(';'):
            statement = '\n'.join(current_statement)
            if statement.strip():
                statements.append(statement)
            current_statement = []
    
    # Execute each statement
    for statement in statements:
        if statement.strip():
            connection.execute(op.text(statement))


def downgrade() -> None:
    """Downgrade not implemented for raw SQL files"""
    # To implement downgrade, create separate SQL files for rollback
    pass

