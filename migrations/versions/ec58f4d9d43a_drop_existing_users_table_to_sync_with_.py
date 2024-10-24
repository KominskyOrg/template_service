"""Drop existing users table to sync with migrations

Revision ID: ec58f4d9d43a
Revises: 0a35a6a9b735
Create Date: 2024-10-14 23:17:25.779702

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec58f4d9d43a'
down_revision = '0a35a6a9b735'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing users table
    op.execute('DROP TABLE IF EXISTS users')
    # Recreate the users table as per the initial migration
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=150), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=150), nullable=False),
        sa.Column('last_name', sa.String(length=150), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

def downgrade():
    # Drop the users table
    op.drop_table('users')