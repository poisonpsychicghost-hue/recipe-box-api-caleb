"""Add example_image_link to Recipe

Revision ID: 8ef8f36675f2
Revises: 5690a8557062
Create Date: 2026-10-20 12:07:25.452207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ef8f36675f2'
down_revision = '5690a8557062'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('example_image_link', sa.String(length=255), nullable=True))
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('title',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.alter_column('ingredients',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.alter_column('instructions',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False,
               existing_server_default=sa.text("('')"))
        batch_op.create_unique_constraint("uq_recipes_example_image_link", ['example_image_link'])

    # ### end Alembic commands ###


def downgrade():

    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.drop_constraint("uq_recipes_example_image_link", type_='unique')
        batch_op.alter_column('instructions',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False,
               existing_server_default=sa.text("('')"))
        batch_op.alter_column('ingredients',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
        batch_op.alter_column('title',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)
        batch_op.drop_column('example_image_link')

    # ### end Alembic commands ###
