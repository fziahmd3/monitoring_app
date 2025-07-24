"""ubah tabel Santri: nis->kode_santri, kelas->tingkatan

Revision ID: fb677578c964
Revises: b98e0399a969
Create Date: 2025-07-24 18:40:51.916290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb677578c964'
down_revision = 'b98e0399a969'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Santri', sa.Column('kode_santri', sa.String(length=20), nullable=False))
    op.add_column('Santri', sa.Column('tingkatan', sa.String(length=50), nullable=False))
    op.drop_column('Santri', 'nis')
    op.drop_column('Santri', 'kelas')


def downgrade():
    op.add_column('Santri', sa.Column('nis', sa.String(length=20), nullable=False))
    op.add_column('Santri', sa.Column('kelas', sa.String(length=50), nullable=False))
    op.drop_column('Santri', 'kode_santri')
    op.drop_column('Santri', 'tingkatan')
