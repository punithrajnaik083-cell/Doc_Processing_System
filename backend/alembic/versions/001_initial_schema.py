
"""Initial database schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-11-15 13:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1. Define ENUM types.
    # Do not manually call .create().
    # SQLAlchemy creates these types when their tables are created.

    doc_status = postgresql.ENUM(
        'queued',
        'processing',
        'valid',
        'needs_review',
        'failed',
        name='document_status'
    )

    flag_level = postgresql.ENUM(
        'error',
        'warning',
        'info',
        name='flag_level'
    )

    # 2. batches table
    op.create_table(
        'batches',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False
        ),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. documents table
    op.create_table(
        'documents',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False
        ),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('filename', sa.Text(), nullable=False),
        sa.Column('ext', sa.Text(), nullable=False),
        sa.Column('mime_type', sa.Text(), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('sha256', sa.Text(), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=True),
        sa.Column('preview_path', sa.Text(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),

        # Reuse the ENUM object defined above.
        sa.Column(
            'status',
            doc_status,
            server_default='queued',
            nullable=False
        ),

        sa.Column('failure_stage', sa.Text(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('doc_type', sa.Text(), nullable=True),
        sa.Column('read_method', sa.Text(), nullable=True),
        sa.Column('ocr_confidence', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('engine', sa.Text(), nullable=True),
        sa.Column('ai_model', sa.Text(), nullable=True),
        sa.Column('ai_input_tokens', sa.Integer(), server_default='0', nullable=False),
        sa.Column('ai_output_tokens', sa.Integer(), server_default='0', nullable=False),
        sa.Column('attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('processing_ms', sa.Integer(), nullable=True),
        sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['batch_id'],
            ['batches.id'],
            ondelete='SET NULL'
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        'ix_documents_user_id_status',
        'documents',
        ['user_id', 'status']
    )

    op.create_index(
        'ix_documents_user_id_created_at_desc',
        'documents',
        ['user_id', sa.text('created_at DESC')]
    )

    op.create_index(
        'ix_documents_sha256',
        'documents',
        ['sha256']
    )

    # 4. extracted_fields table
    op.create_table(
        'extracted_fields',
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doc_no', sa.Text(), nullable=True),
        sa.Column('doc_date', sa.Date(), nullable=True),
        sa.Column('vendor_name', sa.Text(), nullable=True),
        sa.Column('vendor_gstin', sa.Text(), nullable=True),
        sa.Column('buyer_name', sa.Text(), nullable=True),
        sa.Column('buyer_gstin', sa.Text(), nullable=True),
        sa.Column('place_of_supply', sa.Text(), nullable=True),
        sa.Column('subtotal', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('cgst', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('sgst', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('igst', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('round_off', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('total', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('currency', sa.CHAR(length=3), server_default='INR', nullable=False),
        sa.Column('financial_year', sa.Text(), nullable=True),
        sa.Column(
            'sources',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False
        ),
        sa.Column('ai_raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('rules_raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_note', sa.Text(), nullable=True),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['document_id'],
            ['documents.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('document_id')
    )

    op.create_index(
        'ix_extracted_fields_vendor_gstin_doc_no',
        'extracted_fields',
        ['vendor_gstin', 'doc_no']
    )

    # 5. validation_flags table
    op.create_table(
        'validation_flags',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False
        ),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Reuse the ENUM object defined above.
        sa.Column('level', flag_level, nullable=False),

        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('field', sa.Text(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['document_id'],
            ['documents.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. processing_events table
    op.create_table(
        'processing_events',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False
        ),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stage', sa.Text(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['document_id'],
            ['documents.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. field_edits table
    op.create_table(
        'field_edits',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False
        ),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field', sa.Text(), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('edited_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            'edited_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['document_id'],
            ['documents.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. worker_heartbeat table
    op.create_table(
        'worker_heartbeat',
        sa.Column('id', sa.Integer(), server_default='1', nullable=False),
        sa.Column(
            'beat_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:

    # Drop tables in reverse dependency order.
    op.drop_table('worker_heartbeat')
    op.drop_table('field_edits')
    op.drop_table('processing_events')
    op.drop_table('validation_flags')
    op.drop_table('extracted_fields')
    op.drop_table('documents')
    op.drop_table('batches')

    # Drop ENUM types after their dependent tables.
    op.execute('DROP TYPE IF EXISTS flag_level')
    op.execute('DROP TYPE IF EXISTS document_status')
