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
    
    # Parse SQL into individual statements, handling dollar-quoted strings
    statements = _parse_sql_statements(sql)
    
    # Get the raw psycopg2 connection
    connection = op.get_bind().connection
    raw_connection = connection.connection
    
    # Execute each statement separately
    with raw_connection.cursor() as cursor:
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
        raw_connection.commit()


def _parse_sql_statements(sql: str) -> list[str]:
    """
    Parse SQL into individual statements, properly handling dollar-quoted strings.
    Returns a list of SQL statements.
    """
    statements = []
    current_statement = []
    in_dollar_quote = False
    dollar_tag = None
    i = 0
    
    while i < len(sql):
        char = sql[i]
        
        # Check for dollar-quoted string start/end
        if char == '$' and i + 1 < len(sql):
            # Look for $$ or $tag$
            j = i + 1
            # Check for simple $$
            while j < len(sql) and sql[j] == '$':
                j += 1
            
            if j > i + 1:
                # Found $$ - simple dollar quote
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
                # Check for $tag$ pattern
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
        
        # If we're not in a dollar-quoted string and find a semicolon, end the statement
        if not in_dollar_quote and char == ';':
            statement = ''.join(current_statement).strip()
            # Remove leading comment lines but keep the actual SQL statement
            # Split by newlines, filter out comment-only lines, rejoin
            lines = statement.split('\n')
            sql_lines = [line for line in lines if line.strip() and not line.strip().startswith('--')]
            if sql_lines:
                # Rejoin non-comment lines
                clean_statement = '\n'.join(sql_lines).strip()
                if clean_statement:
                    statements.append(clean_statement)
            current_statement = []
        
        i += 1
    
    # Handle any remaining statement
    if current_statement:
        statement = ''.join(current_statement).strip()
        # Remove leading comment lines
        lines = statement.split('\n')
        sql_lines = [line for line in lines if line.strip() and not line.strip().startswith('--')]
        if sql_lines:
            clean_statement = '\n'.join(sql_lines).strip()
            if clean_statement:
                statements.append(clean_statement)
    
    return statements


def downgrade() -> None:
    """Downgrade not implemented for raw SQL files"""
    # To implement downgrade, create separate SQL files for rollback
    pass

