"""empty message

Revision ID: 719f2d775814
Revises: b9e258bbdf3d
Create Date: 2017-03-18 20:00:14.398233

"""

# revision identifiers, used by Alembic.
revision = '719f2d775814'
down_revision = 'b9e258bbdf3d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('student_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('teacher_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('school', sa.String(length=40), nullable=True),
    sa.Column('major', sa.String(length=40), nullable=True),
    sa.Column('detail', sa.String(length=1000), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('teacher_info')
    op.drop_table('student_info')
    # ### end Alembic commands ###
