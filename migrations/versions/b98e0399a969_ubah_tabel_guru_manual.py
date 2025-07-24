"""ubah tabel Guru manual

Revision ID: b98e0399a969
Revises: e449d24b1015
Create Date: 2025-07-24 18:19:44.475157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b98e0399a969'
down_revision = 'e449d24b1015'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Guru', sa.Column('kode_guru', sa.String(length=20), nullable=False))
    op.add_column('Guru', sa.Column('status_pengajar', sa.String(length=50), nullable=True))
    op.drop_column('Guru', 'nip')
    op.drop_column('Guru', 'pendidikan_terakhir')


def downgrade():
    op.add_column('Guru', sa.Column('nip', sa.String(length=20), nullable=False))
    op.add_column('Guru', sa.Column('pendidikan_terakhir', sa.String(length=50), nullable=True))
    op.drop_column('Guru', 'kode_guru')
    op.drop_column('Guru', 'status_pengajar')
