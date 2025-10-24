"""seeding process type table

Revision ID: 1ba032ea912a
Revises: 2ce70f64a2ed
Create Date: 2025-09-02 13:09:41.799954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ba032ea912a'
down_revision: Union[str, Sequence[str], None] = '2ce70f64a2ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("SET IDENTITY_INSERT process_type ON")

    process_type = sa.sql.table(
        'process_type',
        sa.Column('id', sa.Integer),
        sa.Column('title', sa.String),
    )

    op.bulk_insert(
        process_type,
        [
            {'id': -1,  'title': 'Error'},
            {'id': 1,  'title': 'Start Process'},
            {'id': 2,  'title': 'Download File'},
            {'id': 3,  'title': 'Parse Document'},
            {'id': 4,  'title': 'Extract Images'},
            {'id': 5,  'title': 'Upload Images'},
            {'id': 6,  'title': 'MD to DB'},
            {'id': 7,  'title': 'Image to DB'},
            {'id': 8, 'title': 'Process Complete'},
        ]
    )

    # Turn off identity insert
    op.execute("SET IDENTITY_INSERT process_type OFF")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "DELETE FROM process_type WHERE id IN (1,2,3,4,5,6,7,8,-1)"
    )
