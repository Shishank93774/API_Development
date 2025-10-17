"""add fkey for owner in posts

Revision ID: 46d324e71366
Revises: 52c8a659d0e0
Create Date: 2025-10-17 10:17:41.947817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46d324e71366'
down_revision: Union[str, Sequence[str], None] = '52c8a659d0e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key(constraint_name='posts_users_fkey',
                          source_table='posts',
                          referent_table='users',
                          local_cols=['owner_id'],
                          remote_cols=['id'],
                          ondelete='CASCADE'
                          )
    pass


def downgrade() -> None:
    op.drop_constraint('posts_users_fkey', 'posts')
    op.drop_column('posts', 'owner_id')
    pass
