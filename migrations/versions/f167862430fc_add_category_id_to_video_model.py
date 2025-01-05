from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f167862430fc'
down_revision = '834e94d73a01'
branch_labels = None
depends_on = None

def upgrade():
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

    # Remove the 'upvotes' column from the post table if it exists
    inspector = sa.inspect(op.get_bind())
    existing_columns_post = [col['name'] for col in inspector.get_columns('post')]
    with op.batch_alter_table('post', schema=None) as batch_op:
        if 'upvotes' in existing_columns_post:
            batch_op.drop_column('upvotes')

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

    # Add the 'upvotes' column back to the post table
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('upvotes', sa.Integer(), nullable=True))