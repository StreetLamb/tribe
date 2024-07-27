"""Rename provider names in member table to new name

Revision ID: 6e7c33ddf30f
Revises: 0a354b5c6f6c
Create Date: 2024-07-27 04:29:51.886906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e7c33ddf30f'
down_revision = '0a354b5c6f6c'
branch_labels = None
depends_on = None


def upgrade():
    # Mapping of old provider names to new provider names
    mapping = {
        'ChatOpenAI': 'openai',
        'ChatAnthropic': 'anthropic',
    }
    
    # Rename each provider name according to the mapping
    for old_name, new_name in mapping.items():
        op.execute(f"UPDATE member SET provider = '{new_name}' WHERE provider = '{old_name}'")


def downgrade():
    # Mapping of new provider names back to old provider names
    mapping = {
        'openai': 'ChatOpenAI',
        'anthropic': 'ChatAnthropic',
    }
    
    # Revert each provider name according to the mapping
    for new_name, old_name in mapping.items():
        op.execute(f"UPDATE member SET provider = '{old_name}' WHERE provider = '{new_name}'")