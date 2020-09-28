import sqlalchemy as sa

from alembic import op

from lib.util_datetime import tzware_datetime
from lib.util_sqlalchemy import AwareDateTime


"""
added verified

Revision ID: 24bd90246d4a
Revises: 
Create Date: 2020-09-28 09:44:49.158748
"""

# Revision identifiers, used by Alembic.
revision = '24bd90246d4a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('verified', sa.Boolean))
    
def downgrade():
    op.drop_column('users', 'verified')

