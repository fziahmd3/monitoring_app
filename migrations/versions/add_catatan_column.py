"""add catatan column to PenilaianHafalan

Revision ID: add_catatan_column
Revises: add_guru_id_penilaian
Create Date: 2025-07-31 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_catatan_column'
down_revision = 'add_guru_id_penilaian'
branch_labels = None
depends_on = None


def upgrade():
    # Tambahkan kolom catatan ke tabel PenilaianHafalan
    op.add_column('PenilaianHafalan', sa.Column('catatan', sa.Text(), nullable=True))


def downgrade():
    # Hapus kolom catatan dari tabel PenilaianHafalan
    op.drop_column('PenilaianHafalan', 'catatan') 