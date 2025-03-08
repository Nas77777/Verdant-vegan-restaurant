"""remove foreign key column from dining_areas

Revision ID: 85759f24879d
Revises: c2cfd25046dd
Create Date: 2025-03-05 16:38:14.571033

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85759f24879d'
down_revision: Union[str, None] = 'c2cfd25046dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
