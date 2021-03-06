"""empty message

Revision ID: 786cb446d62f
Revises: 
Create Date: 2018-08-19 10:41:54.075777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '786cb446d62f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crypto_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('key', sa.String(length=1500), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('transactionId', sa.Integer(), nullable=False),
    sa.Column('senderId', sa.Integer(), nullable=True),
    sa.Column('receiverId', sa.Integer(), nullable=True),
    sa.Column('senderBill', sa.String(length=200), nullable=True),
    sa.Column('receiverBill', sa.String(length=200), nullable=True),
    sa.Column('transferAmount', sa.String(length=200), nullable=True),
    sa.Column('message', sa.String(length=1200), nullable=True),
    sa.Column('date', sa.String(length=1200), nullable=True),
    sa.PrimaryKeyConstraint('transactionId'),
    sa.UniqueConstraint('transactionId')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('surname', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(length=255), nullable=True),
    sa.Column('password_hash', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('billfold',
    sa.Column('billfold_number', sa.String(length=200), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('wallet', sa.String(length=30), nullable=True),
    sa.Column('balance', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('billfold_number'),
    sa.UniqueConstraint('billfold_number')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('billfold')
    op.drop_table('user')
    op.drop_table('transactions')
    op.drop_table('crypto_info')
    # ### end Alembic commands ###
