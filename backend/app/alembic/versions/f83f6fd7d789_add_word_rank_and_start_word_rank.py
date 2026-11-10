"""add word.rank and settings.start_word_rank

Lets a user pick a starting "level" (start from word 1000/2000/...).

Adds `word.rank` as the word's frequency rank, decoupled from its primary
key `id`. Until now the import script (parse_git_words.py) abused the PK
itself to carry frequency rank by inserting explicit `id` values, which
never advanced the `word_id_seq` sequence - any future insert that let the
PK auto-generate (tests, an admin-added word, ...) would collide with an
already-used id. Backfills `rank` from the existing `id` values (they were
already assigned from the source ranking) and re-syncs the sequence so the
PK is safe to auto-generate again.

Also adds `settings.start_word_rank`, the per-user chosen starting rank.

Revision ID: f83f6fd7d789
Revises: b84319062ccc
Create Date: 2026-09-25 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f83f6fd7d789'
down_revision = 'b84319062ccc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('word', sa.Column('rank', sa.Integer(), nullable=True))
    op.execute('UPDATE word SET rank = id')
    op.alter_column('word', 'rank', nullable=False)
    op.create_unique_constraint('uq_word_rank', 'word', ['rank'])
    op.create_index(op.f('ix_word_rank'), 'word', ['rank'], unique=False)

    # `id` values were inserted explicitly by the import script, which never
    # advances a sequence-backed default. Re-sync it so future auto-generated
    # ids don't collide with existing rows.
    op.execute(
        "SELECT setval('word_id_seq', COALESCE((SELECT MAX(id) FROM word), 1))"
    )

    op.add_column(
        'settings',
        sa.Column(
            'start_word_rank', sa.Integer(), nullable=False, server_default='0'
        ),
    )
    op.create_check_constraint(
        'check_start_word_rank_non_negative', 'settings', 'start_word_rank >= 0'
    )


def downgrade():
    op.drop_constraint(
        'check_start_word_rank_non_negative', 'settings', type_='check'
    )
    op.drop_column('settings', 'start_word_rank')

    op.drop_index(op.f('ix_word_rank'), table_name='word')
    op.drop_constraint('uq_word_rank', 'word', type_='unique')
    op.drop_column('word', 'rank')
