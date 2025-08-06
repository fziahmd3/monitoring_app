"""add guru_id column to PenilaianHafalan table

Revision ID: add_guru_id_penilaian
Revises: 7ec29af99622
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_guru_id_penilaian'
down_revision = '7ec29af99622'
branch_labels = None
depends_on = None

def upgrade():
    # Add guru_id column to PenilaianHafalan table
    op.add_column('PenilaianHafalan', sa.Column('guru_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_penilaianhafalan_guru_id',
        'PenilaianHafalan', 'Guru',
        ['guru_id'], ['guru_id']
    )

def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('fk_penilaianhafalan_guru_id', 'PenilaianHafalan', type_='foreignkey')
    
    # Remove guru_id column
    op.drop_column('PenilaianHafalan', 'guru_id') 