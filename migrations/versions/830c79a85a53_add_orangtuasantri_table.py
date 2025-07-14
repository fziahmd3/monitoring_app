"""Add OrangTuaSantri table

Revision ID: 830c79a85a53
Revises: 67d885446952
Create Date: 2025-07-14 14:41:50.660271

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '830c79a85a53'
down_revision = '67d885446952'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'OrangTuaSantri',
        sa.Column('ortu_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nama', sa.String(length=100), nullable=False),
        sa.Column('alamat', sa.String(length=255), nullable=True),
        sa.Column('nama_santri', sa.String(length=100), nullable=False),
        sa.Column('nomor_telepon', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('ortu_id')
    )

def downgrade():
    op.drop_table('OrangTuaSantri')
