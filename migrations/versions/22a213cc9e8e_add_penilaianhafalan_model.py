"""add PenilaianHafalan model

Revision ID: 22a213cc9e8e
Revises: a718b6ef2d3d
Create Date: 2025-07-18 13:07:25.230542

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '22a213cc9e8e'
down_revision = 'a718b6ef2d3d'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('PenilaianHafalan',
        sa.Column('penilaian_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('santri_id', sa.Integer(), nullable=False),
        sa.Column('surat', sa.String(length=50), nullable=False),
        sa.Column('dari_ayat', sa.Integer(), nullable=False),
        sa.Column('sampai_ayat', sa.Integer(), nullable=False),
        sa.Column('penilaian_tajwid', sa.String(length=20), nullable=False),
        sa.Column('tanggal_penilaian', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['santri_id'], ['Santri.santri_id'], ),
        sa.PrimaryKeyConstraint('penilaian_id')
    )

def downgrade():
    op.drop_table('PenilaianHafalan')
