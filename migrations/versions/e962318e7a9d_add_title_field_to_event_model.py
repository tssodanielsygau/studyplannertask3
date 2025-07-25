"""Add title field to event model

Revision ID: e962318e7a9d
Revises: 
Create Date: 2025-07-22 18:34:24.093219

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e962318e7a9d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(length=150), nullable=False))
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('category')
        batch_op.drop_column('name')

    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=sa.VARCHAR(length=10000),
               type_=sa.Text(),
               existing_nullable=True)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('google_token')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('google_token', sa.TEXT(), nullable=True))

    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=10000),
               existing_nullable=True)

    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('category', sa.VARCHAR(length=50), nullable=True))
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               nullable=True)
        batch_op.drop_column('title')

    # ### end Alembic commands ###
