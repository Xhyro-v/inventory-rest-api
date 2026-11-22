"""Add new enum Reason for product stock adjustment

Revision ID: b3c20bdae1db
Revises: f74066d90fcc
Create Date: 2026-11-22 14:08:29.429473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c20bdae1db'
down_revision: Union[str, Sequence[str], None] = 'f74066d90fcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE reason ADD VALUE IF NOT EXISTS 'CANCEL_RESTOCK'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
