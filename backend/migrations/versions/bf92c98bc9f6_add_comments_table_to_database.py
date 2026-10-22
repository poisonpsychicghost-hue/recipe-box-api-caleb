"""Add Comments Table to database

Revision ID: bf92c98bc9f6
Revises: 8ef8f36675f2
Create Date: 2026-10-21 19:32:33.194663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf92c98bc9f6'
down_revision = '8ef8f36675f2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('comment_text', sa.String(length=320), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('poster_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['poster_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_table('comments')
    # ### end Alembic commands ###
