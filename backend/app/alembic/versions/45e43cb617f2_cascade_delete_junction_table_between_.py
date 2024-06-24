"""cascade delete junction table between members-skills and members-uploads

Revision ID: 45e43cb617f2
Revises: bfb17969c4ed
Create Date: 2024-06-23 16:08:18.903068

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '45e43cb617f2'
down_revision = 'bfb17969c4ed'
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing foreign key constraints
    op.drop_constraint('memberskillslink_member_id_fkey', 'memberskillslink', type_='foreignkey')
    op.drop_constraint('memberskillslink_skill_id_fkey', 'memberskillslink', type_='foreignkey')
    op.drop_constraint('memberuploadslink_member_id_fkey', 'memberuploadslink', type_='foreignkey')
    op.drop_constraint('memberuploadslink_upload_id_fkey', 'memberuploadslink', type_='foreignkey')

    # Create new foreign key constraints with ON DELETE CASCADE
    op.create_foreign_key(
        'memberskillslink_member_id_fkey', 'memberskillslink', 'member', ['member_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(
        'memberskillslink_skill_id_fkey', 'memberskillslink', 'skill', ['skill_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(
        'memberuploadslink_member_id_fkey', 'memberuploadslink', 'member', ['member_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(
        'memberuploadslink_upload_id_fkey', 'memberuploadslink', 'upload', ['upload_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # Drop the foreign key constraints with ON DELETE CASCADE
    op.drop_constraint('memberskillslink_member_id_fkey', 'memberskillslink', type_='foreignkey')
    op.drop_constraint('memberskillslink_skill_id_fkey', 'memberskillslink', type_='foreignkey')
    op.drop_constraint('memberuploadslink_member_id_fkey', 'memberuploadslink', type_='foreignkey')
    op.drop_constraint('memberuploadslink_upload_id_fkey', 'memberuploadslink', type_='foreignkey')

    # Recreate the original foreign key constraints without ON DELETE CASCADE
    op.create_foreign_key(
        'memberskillslink_member_id_fkey', 'memberskillslink', 'member', ['member_id'], ['id'])
    op.create_foreign_key(
        'memberskillslink_skill_id_fkey', 'memberskillslink', 'skill', ['skill_id'], ['id'])
    op.create_foreign_key(
        'memberuploadslink_member_id_fkey', 'memberuploadslink', 'member', ['member_id'], ['id'])
    op.create_foreign_key(
        'memberuploadslink_upload_id_fkey', 'memberuploadslink', 'upload', ['upload_id'], ['id'])
