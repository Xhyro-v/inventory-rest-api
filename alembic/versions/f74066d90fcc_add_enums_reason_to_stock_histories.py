"""Add enums reason to stock histories

Revision ID: f74066d90fcc
Revises: 542bd37e462b
Create Date: 2026-11-21 22:38:05.074569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f74066d90fcc'
down_revision: Union[str, Sequence[str], None] = '542bd37e462b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE reason ADD VALUE IF NOT EXISTS 'BUY'")
        op.execute("ALTER TYPE reason ADD VALUE IF NOT EXISTS 'RESTOCK'")
        op.execute("ALTER TYPE reason ADD VALUE IF NOT EXISTS 'DAMAGED'")
        op.execute("ALTER TYPE reason ADD VALUE IF NOT EXISTS 'LOST'")
        op.execute("ALTER TYPE reason ADD VALUE IF NOT EXISTS 'MANUAL_CORRECTION'")






def downgrade() -> None:
    """Downgrade schema."""
    # Postgres can't drop a single enum value, so this is intentionally a no-op.
    pass