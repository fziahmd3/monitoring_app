"""Ubah nama_santri jadi santri_id sebagai foreign key

Revision ID: a718b6ef2d3d
Revises: 830c79a85a53
Create Date: 2025-07-14 16:27:26.938393

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a718b6ef2d3d'
down_revision = '830c79a85a53'
branch_labels = None
depends_on = None


def upgrade():
    # Tambah kolom santri_id
    op.add_column('OrangTuaSantri', sa.Column('santri_id', sa.Integer(), nullable=True))
    # Buat foreign key ke Santri
    op.create_foreign_key('fk_ortu_santri', 'OrangTuaSantri', 'Santri', ['santri_id'], ['santri_id'])
    # Hapus kolom nama_santri (jika belum dihapus manual)
    # op.drop_column('OrangTuaSantri', 'nama_santri')

def downgrade():
    # Tambah kembali kolom nama_santri
    op.add_column('OrangTuaSantri', sa.Column('nama_santri', sa.String(length=100), nullable=False))
    # Hapus foreign key dan kolom santri_id
    op.drop_constraint('fk_ortu_santri', 'OrangTuaSantri', type_='foreignkey')
    op.drop_column('OrangTuaSantri', 'santri_id')
