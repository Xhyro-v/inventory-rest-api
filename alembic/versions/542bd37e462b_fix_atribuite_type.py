"""fix atribuite type

Revision ID: 542bd37e462b
Revises: 1b2eb6f35dc7
Create Date: 2026-10-13 21:53:31.420775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '542bd37e462b'
down_revision: Union[str, Sequence[str], None] = '1b2eb6f35dc7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
