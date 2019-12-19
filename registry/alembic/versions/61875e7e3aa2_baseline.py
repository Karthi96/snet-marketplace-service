"""baseline

Revision ID: 61875e7e3aa2
Revises: 
Create Date: 2019-12-18 17:57:38.819081

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '61875e7e3aa2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
    sa.Column('row_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=128), nullable=False),
    sa.Column('id', sa.VARCHAR(length=128), nullable=False),
    sa.Column('org_uuid', sa.VARCHAR(length=128), nullable=True),
    sa.Column('payment_address', sa.VARCHAR(length=128), nullable=False),
    sa.Column('payment_config', mysql.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('row_id')
    )
    op.create_table('org_member',
    sa.Column('row_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('org_uuid', sa.VARCHAR(length=128), nullable=True),
    sa.Column('role', sa.VARCHAR(length=128), nullable=True),
    sa.Column('username', sa.VARCHAR(length=128), nullable=True),
    sa.PrimaryKeyConstraint('row_id')
    )
    op.create_table('organization',
    sa.Column('row_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=128), nullable=False),
    sa.Column('org_uuid', sa.VARCHAR(length=128), nullable=True),
    sa.Column('id', sa.VARCHAR(length=128), nullable=False),
    sa.Column('type', sa.VARCHAR(length=128), nullable=False),
    sa.Column('description', sa.VARCHAR(length=1024), nullable=False),
    sa.Column('short_description', sa.VARCHAR(length=1024), nullable=False),
    sa.Column('url', sa.VARCHAR(length=512), nullable=False),
    sa.Column('contacts', mysql.JSON(), nullable=False),
    sa.Column('assets', mysql.JSON(), nullable=False),
    sa.Column('ipfs_hash', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('row_id')
    )
    op.create_table('organization_hostory',
    sa.Column('row_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=128), nullable=False),
    sa.Column('org_uuid', sa.VARCHAR(length=128), nullable=True),
    sa.Column('id', sa.VARCHAR(length=128), nullable=False),
    sa.Column('type', sa.VARCHAR(length=128), nullable=False),
    sa.Column('description', sa.VARCHAR(length=1024), nullable=False),
    sa.Column('short_description', sa.VARCHAR(length=1024), nullable=False),
    sa.Column('url', sa.VARCHAR(length=512), nullable=False),
    sa.Column('contacts', mysql.JSON(), nullable=False),
    sa.Column('assets', mysql.JSON(), nullable=False),
    sa.Column('ipfs_hash', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('row_id')
    )
    op.create_table('organization_review_workflow',
    sa.Column('row_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('organization_row_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.VARCHAR(length=128), nullable=False),
    sa.Column('created_by', sa.VARCHAR(length=128), nullable=False),
    sa.Column('updated_by', sa.VARCHAR(length=128), nullable=False),
    sa.Column('approved_by', sa.VARCHAR(length=128), nullable=True),
    sa.Column('created_on', mysql.TIMESTAMP(), nullable=True),
    sa.Column('modified_on', mysql.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('row_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('organization_review_workflow')
    op.drop_table('organization_hostory')
    op.drop_table('organization')
    op.drop_table('org_member')
    op.drop_table('groups')
    # ### end Alembic commands ###
