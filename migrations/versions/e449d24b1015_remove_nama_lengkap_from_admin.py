"""remove nama_lengkap from admin

Revision ID: e449d24b1015
Revises: 22a213cc9e8e
Create Date: 2025-07-18 14:22:00.396159

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e449d24b1015'
down_revision = '22a213cc9e8e'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('Admin', 'nama_lengkap')

def downgrade():
    op.add_column('Admin', sa.Column('nama_lengkap', sa.String(length=100), nullable=True))
