"""add create date field

Revision ID: 9ba09c8f2eb1
Revises: edec83074e5e
Create Date: 2023-07-15 22:05:00.268525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ba09c8f2eb1'
down_revision = 'edec83074e5e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account_used_traffic', sa.Column('created_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('account_used_traffic', 'created_at')
    # ### end Alembic commands ###
