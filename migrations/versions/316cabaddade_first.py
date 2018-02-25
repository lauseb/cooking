"""first

Revision ID: 316cabaddade
Revises: 
Create Date: 2018-02-21 08:51:16.985795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '316cabaddade'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ingredient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingredient_name'), 'ingredient', ['name'], unique=True)
    op.create_table('recipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('steps', sa.UnicodeText(), nullable=True),
    sa.Column('servings', sa.Integer(), nullable=True),
    sa.Column('cooking_temperature', sa.Integer(), nullable=True),
    sa.Column('cooking_time', sa.Integer(), nullable=True),
    sa.Column('prep_time', sa.Integer(), nullable=True),
    sa.Column('upcoming', sa.Boolean(), nullable=True),
    sa.Column('upcoming_servings', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipe_name'), 'recipe', ['name'], unique=False)
    op.create_index(op.f('ix_recipe_upcoming'), 'recipe', ['upcoming'], unique=False)
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tag_name'), 'tag', ['name'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('quantity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit', sa.String(length=32), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('ingredient_id', sa.Integer(), nullable=True),
    sa.Column('recipe_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredient.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recipe_tags',
    sa.Column('recipe_id', sa.Integer(), nullable=True),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipe_tags')
    op.drop_table('quantity')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_tag_name'), table_name='tag')
    op.drop_table('tag')
    op.drop_index(op.f('ix_recipe_upcoming'), table_name='recipe')
    op.drop_index(op.f('ix_recipe_name'), table_name='recipe')
    op.drop_table('recipe')
    op.drop_index(op.f('ix_ingredient_name'), table_name='ingredient')
    op.drop_table('ingredient')
    # ### end Alembic commands ###