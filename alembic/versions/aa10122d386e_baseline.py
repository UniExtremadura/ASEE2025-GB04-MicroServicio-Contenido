"""baseline

Revision ID: aa10122d386e
Revises: 96e4c98139f3
Create Date: 2025-11-04 23:36:38.943474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa10122d386e'
down_revision: Union[str, None] = '96e4c98139f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
