"""make telegram_id the sole primary key of user

The `user` table ended up with a composite primary key of
(telegram_id, id) because the shared `Base.id` autoincrement column was
never overridden for the User model. Every other table's foreign key
already points at user.telegram_id (never user.id), so telegram_id is the
table's real identity; this migration drops the redundant `id` column from
the primary key and keeps it as a plain unique, non-null column.

Revision ID: b84319062ccc
Revises: 9d9d5f40348d
Create Date: 2026-09-25 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b84319062ccc'
down_revision = '9d9d5f40348d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('pk_user', 'user', type_='primary')
    op.create_primary_key('pk_user', 'user', ['telegram_id'])
    op.create_unique_constraint('uq_user_id', 'user', ['id'])


def downgrade():
    op.drop_constraint('uq_user_id', 'user', type_='unique')
    op.drop_constraint('pk_user', 'user', type_='primary')
    op.create_primary_key('pk_user', 'user', ['telegram_id', 'id'])
