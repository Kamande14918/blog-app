"""Add subscriber_count to channel

Revision ID: bac8af946f17
Revises: f167862430fc
Create Date: 2025-06-26 00:01:14.401768

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bac8af946f17'
down_revision = 'f167862430fc'
branch_labels = None
depends_on = None


def upgrade():
    # Conditionally drop the 'admin' table if it exists
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE() AND LOWER(TABLE_NAME) = 'admin'"))
    if result.fetchone():
        op.drop_table('admin')

    # Check if the 'bins' table exists before dropping constraints or the table
    result = conn.execute(sa.text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE() AND LOWER(TABLE_NAME) = 'bins'"))
    if result.fetchone():
        # Drop the foreign key constraint 'bins_ibfk_1' on the 'bins' table
        with op.batch_alter_table('bins', schema=None) as batch_op:
            batch_op.drop_constraint('bins_ibfk_1', type_='foreignkey')

        # Drop the 'bins' table
        op.drop_table('bins')

    # Check if the 'users' table exists before dropping it
    result = conn.execute(sa.text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE() AND LOWER(TABLE_NAME) = 'users'"))
    if result.fetchone():
        # Drop the 'users' table
        op.drop_table('users')

    # Add new columns and modify existing tables
    # Check if the 'subscriber_count' column exists before adding it
    result = conn.execute(sa.text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'channel' AND COLUMN_NAME = 'subscriber_count'"))
    if not result.fetchone():
        with op.batch_alter_table('channel', schema=None) as batch_op:
            batch_op.add_column(sa.Column('subscriber_count', sa.Integer(), nullable=True))

    # Check if the 'text' column exists before adding it
    result = conn.execute(sa.text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'comment' AND COLUMN_NAME = 'text'"))
    if not result.fetchone():
        with op.batch_alter_table('comment', schema=None) as batch_op:
            batch_op.add_column(sa.Column('text', sa.Text(), nullable=False))

    with op.batch_alter_table('comment', schema=None) as batch_op:
        # Add 'comment_date' with a default value first
        batch_op.add_column(sa.Column('comment_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True))

    # Check for invalid datetime values before updating 'comment_date'
    try:
        # Ensure no invalid datetime values exist before altering the column
        invalid_datetime_check = conn.execute(sa.text("SELECT COUNT(*) FROM comment WHERE comment_date = '0000-00-00 00:00:00'"))
        if invalid_datetime_check.scalar() > 0:
            conn.execute(sa.text("UPDATE comment SET comment_date = CURRENT_TIMESTAMP WHERE comment_date = '0000-00-00 00:00:00'"))
    except Exception as e:
        # Log the error and raise it to ensure visibility
        print(f"Error updating invalid datetime values in 'comment_date': {e}")
        raise

    # Update rows with NULL 'comment_date' values
    try:
        conn.execute(sa.text("UPDATE comment SET comment_date = CURRENT_TIMESTAMP WHERE comment_date IS NULL"))
    except Exception as e:
        # Log the error and raise it to ensure visibility
        print(f"Error updating NULL values in 'comment_date': {e}")
        raise

    # Alter 'comment_date' to make it NOT NULL
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.alter_column('comment_date', nullable=False)

        batch_op.alter_column('video_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.drop_constraint(batch_op.f('comment_ibfk_3'), type_='foreignkey')
        batch_op.drop_column('content')
        batch_op.drop_column('post_id')
        batch_op.drop_column('date_posted')

    with op.batch_alter_table('video', schema=None) as batch_op:
        batch_op.add_column(sa.Column('upload_date', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('views', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('duration', sa.Integer(), nullable=False))
        batch_op.alter_column('description',
               existing_type=mysql.TEXT(),
               nullable=True)
        batch_op.drop_column('date_posted')

    with op.batch_alter_table('vote', schema=None) as batch_op:
        batch_op.drop_column('vote_type')

    # Recreate the 'admin' table only if necessary
    if not result.fetchone():
        op.create_table('admin',
            sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
            sa.Column('name', mysql.VARCHAR(length=255), nullable=True),
            sa.Column('scheduled_day', sa.DATE(), nullable=True),
            sa.Column('payment_status', mysql.ENUM('paid', 'pending'), nullable=True),
            sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            mysql_collate='utf8mb4_0900_ai_ci',
            mysql_default_charset='utf8mb4',
            mysql_engine='InnoDB'
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vote', schema=None) as batch_op:
        batch_op.add_column(sa.Column('vote_type', mysql.VARCHAR(length=10), nullable=False))

    with op.batch_alter_table('video', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_posted', mysql.DATETIME(), nullable=False))
        batch_op.alter_column('description',
               existing_type=mysql.TEXT(),
               nullable=False)
        batch_op.drop_column('duration')
        batch_op.drop_column('views')
        batch_op.drop_column('upload_date')

    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_posted', mysql.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('post_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('content', mysql.TEXT(), nullable=False))
        batch_op.create_foreign_key(batch_op.f('comment_ibfk_3'), 'post', ['post_id'], ['id'])
        batch_op.alter_column('video_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.drop_column('comment_date')
        batch_op.drop_column('text')

    with op.batch_alter_table('channel', schema=None) as batch_op:
        batch_op.drop_column('subscriber_count')

    op.create_table('bins',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('bin_id', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('fill_level', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('location', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('admin_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('timestamp', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['admin.id'], name=op.f('bins_ibfk_2'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('bins_ibfk_1'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('bins', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('bin_id'), ['bin_id'], unique=True)

    op.create_table('users',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('password', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('status', mysql.ENUM('active', 'inactive'), nullable=True),
    sa.Column('otp', mysql.VARCHAR(length=6), nullable=True),
    sa.Column('otp_expiry', mysql.DATETIME(), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('admin',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('scheduled_day', sa.DATE(), nullable=True),
    sa.Column('payment_status', mysql.ENUM('paid', 'pending'), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
