from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '78b3b8f7a63b'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Drop the foreign key constraint on the 'bins' table
    with op.batch_alter_table('bins') as batch_op:
        batch_op.drop_constraint('bins_ibfk_2', type_='foreignkey')

    # Add the 'subscriber_count' column to the 'channel' table
    with op.batch_alter_table('channel') as batch_op:
        batch_op.add_column(sa.Column('subscriber_count', sa.Integer(), nullable=True))

    # Drop the foreign key constraint first
    with op.batch_alter_table('post') as batch_op:
        batch_op.drop_constraint('post_ibfk_2', type_='foreignkey')
    
    # Drop the space table if it exists
    op.execute('DROP TABLE IF EXISTS space')

    # Add the category_id column to the video table
    with op.batch_alter_table('video') as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_video_category', 'category', ['category_id'], ['id'])

    # Drop the tags table if it exists
    op.execute('DROP TABLE IF EXISTS tags')

    # Check if the 'upvotes' column exists before adding it
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('post')]
    if 'upvotes' not in columns:
        with op.batch_alter_table('post', schema=None) as batch_op:
            batch_op.add_column(sa.Column('upvotes', sa.Integer(), nullable=True))

def downgrade():
    # Remove the category_id column from the video table
    with op.batch_alter_table('video') as batch_op:
        batch_op.drop_constraint('fk_video_category', type_='foreignkey')
        batch_op.drop_column('category_id')

    # Recreate the space table
    op.create_table(
        'space',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate the foreign key constraint
    with op.batch_alter_table('post') as batch_op:
        batch_op.create_foreign_key('post_ibfk_2', 'space', ['space_id'], ['id'])

    # Recreate the tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=50), nullable=False)
    )

    # Remove the 'upvotes' column if it exists
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('post')]
    if 'upvotes' in columns:
        with op.batch_alter_table('post', schema=None) as batch_op:
            batch_op.drop_column('upvotes')