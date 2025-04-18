"""remove subject field

Revision ID: 423617f8e7a7
Revises: db213ee73835
Create Date: 2025-04-15 11:27:55.168073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '423617f8e7a7'
down_revision = 'db213ee73835'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_column('subject')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subject', sa.VARCHAR(length=255), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
