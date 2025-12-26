"""indexes_and_constraints

Revision ID: 0020
Revises: 0010
Create Date: 2025-12-25 17:00:00.000000

"""
from alembic import op
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# revision identifiers, used by Alembic.
revision = '0020'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Execute indexes and constraints migration from SQL file"""
    sql_file = project_root / 'db' / 'migration' / '0.0.20__indexes_and_constraints.sql'
    
    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Parse SQL into individual statements
    statements = _parse_sql_statements(sql)
    
    # Get the raw psycopg2 connection
    connection = op.get_bind().connection
    raw_connection = connection.connection
    
    # Execute each statement separately
    with raw_connection.cursor() as cursor:
        for statement in statements:
            if statement.strip() and not statement.strip().startswith('--'):
                cursor.execute(statement)
        raw_connection.commit()


def _parse_sql_statements(sql: str) -> list[str]:
    """Parse SQL into individual statements, handling dollar-quoted strings."""
    statements = []
    current_statement = []
    in_dollar_quote = False
    dollar_tag = None
    i = 0
    
    while i < len(sql):
        char = sql[i]
        
        if char == '$' and i + 1 < len(sql):
            j = i + 1
            while j < len(sql) and sql[j] == '$':
                j += 1
            
            if j > i + 1:
                if not in_dollar_quote:
                    in_dollar_quote = True
                    dollar_tag = None
                else:
                    in_dollar_quote = False
                    dollar_tag = None
                current_statement.append(sql[i:j])
                i = j
                continue
            else:
                tag_end = j
                while tag_end < len(sql) and sql[tag_end] != '$' and (sql[tag_end].isalnum() or sql[tag_end] == '_'):
                    tag_end += 1
                if tag_end < len(sql) and sql[tag_end] == '$':
                    tag = sql[i+1:tag_end]
                    if not in_dollar_quote:
                        in_dollar_quote = True
                        dollar_tag = tag
                    elif dollar_tag == tag:
                        in_dollar_quote = False
                        dollar_tag = None
                    current_statement.append(sql[i:tag_end+1])
                    i = tag_end + 1
                    continue
        
        current_statement.append(char)
        
        if not in_dollar_quote and char == ';':
            statement = ''.join(current_statement).strip()
            # Remove leading comment lines but keep the actual SQL statement
            lines = statement.split('\n')
            sql_lines = [line for line in lines if line.strip() and not line.strip().startswith('--')]
            if sql_lines:
                clean_statement = '\n'.join(sql_lines).strip()
                if clean_statement:
                    statements.append(clean_statement)
            current_statement = []
        
        i += 1
    
    if current_statement:
        statement = ''.join(current_statement).strip()
        lines = statement.split('\n')
        sql_lines = [line for line in lines if line.strip() and not line.strip().startswith('--')]
        if sql_lines:
            clean_statement = '\n'.join(sql_lines).strip()
            if clean_statement:
                statements.append(clean_statement)
    
    return statements


def downgrade() -> None:
    """Downgrade not implemented for raw SQL files"""
    pass

