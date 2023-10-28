"""connectors_table

Revision ID: 0015
Revises: 0014
Create Date: 2023-10-28 09:51:11.574495

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('connectors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('charge_point_id', sa.String(), nullable=False),
    sa.Column('driver_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['charge_point_id'], ['charge_points.id'], ),
    sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
    sa.PrimaryKeyConstraint('id', 'charge_point_id'),
    sa.UniqueConstraint('id', 'charge_point_id')
    )
    op.drop_constraint('charge_points_driver_id_fkey', 'charge_points', type_='foreignkey')
    op.drop_column('charge_points', 'driver_id')
    op.drop_column('charge_points', 'connectors')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('charge_points', sa.Column('connectors', postgresql.ARRAY(postgresql.JSON(astext_type=sa.Text())), autoincrement=False, nullable=True))
    op.add_column('charge_points', sa.Column('driver_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_foreign_key('charge_points_driver_id_fkey', 'charge_points', 'drivers', ['driver_id'], ['id'])
    op.drop_table('connectors')
    # ### end Alembic commands ###