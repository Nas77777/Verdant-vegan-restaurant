"""Remove reservation_id from dining_areas

Revision ID: b9d53a500f80
Revises: 
Create Date: 2025-03-05 17:00:33.446698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9d53a500f80'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dining_areas', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('reservation_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dining_areas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reservation_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key(None, 'reservations', ['reservation_id'], ['id'])

    # ### end Alembic commands ###
