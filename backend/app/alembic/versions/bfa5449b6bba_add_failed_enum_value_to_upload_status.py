"""Add 'Failed' enum value to upload status

Revision ID: bfa5449b6bba
Revises: eab5bf7ec514
Create Date: 2024-06-28 15:18:51.744902

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bfa5449b6bba'
down_revision = 'eab5bf7ec514'
branch_labels = None
depends_on = None


def upgrade():
    # Add new value to the enum type
    op.execute("ALTER TYPE uploadstatus ADD VALUE 'FAILED'")

def downgrade():
    # Downgrade logic to remove the 'FAILED' value is not straightforward
    # Enum types in PostgreSQL cannot remove a value directly
    # So, we need to create a new enum type without 'FAILED', convert the column, and drop the old type

    # Create a new enum type without 'FAILED'
    op.execute("CREATE TYPE uploadstatus_tmp AS ENUM('IN_PROGRESS', 'COMPLETED')")

    # Alter the column to use the new enum type
    op.alter_column(
        'upload',
        'status',
        existing_type=postgresql.ENUM('IN_PROGRESS', 'COMPLETED', 'FAILED', name='uploadstatus'),
        type_=postgresql.ENUM('IN_PROGRESS', 'COMPLETED', name='uploadstatus_tmp'),
        existing_nullable=True
    )

    # Drop the old enum type
    op.execute("DROP TYPE uploadstatus")

    # Rename the new enum type to the old name
    op.execute("ALTER TYPE uploadstatus_tmp RENAME TO uploadstatus")
