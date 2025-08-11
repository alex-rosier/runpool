"""add_game_completion_fields

Revision ID: 625fba49f227
Revises: 7eca48f812c6
Create Date: 2025-08-10 22:15:35.516161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '625fba49f227'
down_revision = '7eca48f812c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table('game') as batch_op:
        # Add new columns to the game table
        batch_op.add_column(sa.Column('status', sa.String(20), nullable=False, server_default='active'))
        batch_op.add_column(sa.Column('end_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('winner_player_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('winner_team_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('tiebreaker_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table('game') as batch_op:
        # Remove columns
        batch_op.drop_column('tiebreaker_notes')
        batch_op.drop_column('winner_team_id')
        batch_op.drop_column('winner_player_id')
        batch_op.drop_column('end_date')
        batch_op.drop_column('status')
