"""roles_and_permissions

Revision ID: 0040
Revises: 0030
Create Date: 2024-12-25 17:00:00.000000

"""
from alembic import op
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# revision identifiers, used by Alembic.
revision = '0040'
down_revision = '0030'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Execute roles and permissions migration from SQL file"""
    sql_file = project_root / 'db' / 'migration' / '0.0.40__roles_and_permissions.sql'
    
    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Execute SQL statements
    connection = op.get_bind()
    statements = []
    current_statement = []
    
    for line in sql.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('--'):
            continue
        current_statement.append(line)
        if stripped.endswith(';'):
            statement = '\n'.join(current_statement)
            if statement.strip():
                statements.append(statement)
            current_statement = []
    
    for statement in statements:
        if statement.strip():
            connection.execute(op.text(statement))


def downgrade() -> None:
    """Downgrade not implemented for raw SQL files"""
    pass

