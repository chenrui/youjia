"""empty message

Revision ID: 8d1092fd912c
Revises: 719f2d775814
Create Date: 2017-03-19 21:24:33.883241

"""

# revision identifiers, used by Alembic.
revision = '8d1092fd912c'
down_revision = '719f2d775814'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('teacher_info', sa.Column('graduated', sa.String(length=1000), nullable=True))
    op.add_column('teacher_info', sa.Column('introduce', sa.String(length=1000), nullable=True))
    op.drop_column('teacher_info', 'school')
    op.drop_column('teacher_info', 'major')
    op.drop_column('teacher_info', 'detail')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('teacher_info', sa.Column('detail', mysql.VARCHAR(length=1000), nullable=True))
    op.add_column('teacher_info', sa.Column('major', mysql.VARCHAR(length=40), nullable=True))
    op.add_column('teacher_info', sa.Column('school', mysql.VARCHAR(length=40), nullable=True))
    op.drop_column('teacher_info', 'introduce')
    op.drop_column('teacher_info', 'graduated')
    # ### end Alembic commands ###
