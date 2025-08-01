"""Add plan_type, plan_document_full_text, summary_of_benefit_coverage, and table_of_contents columns to plans table

Revision ID: 0443cd3babc9
Revises: 
Create Date: 2025-08-01 13:43:58.722653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0443cd3babc9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plans', sa.Column('plan_type', sa.Text(), nullable=True))
    op.add_column('plans', sa.Column('plan_document_full_text', sa.Text(), nullable=True))
    op.add_column('plans', sa.Column('summary_of_benefit_coverage', sa.Text(), nullable=True))
    op.add_column('plans', sa.Column('table_of_contents', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('plans', 'table_of_contents')
    op.drop_column('plans', 'summary_of_benefit_coverage')
    op.drop_column('plans', 'plan_document_full_text')
    op.drop_column('plans', 'plan_type')
    # ### end Alembic commands ###
