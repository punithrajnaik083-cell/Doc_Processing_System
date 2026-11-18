import enum
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Enum,
    CHAR,
    text,
    func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db import Base

class DocumentStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    VALID = "valid"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"

class FlagLevel(str, enum.Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class Batch(Base):
    __tablename__ = "batches"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    documents = relationship("Document", back_populates="batch", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id", ondelete="SET NULL"), nullable=True)
    filename = Column(Text, nullable=False)
    ext = Column(Text, nullable=False)
    mime_type = Column(Text, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=True)
    preview_path = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    status = Column(
        Enum(
            "queued", "processing", "valid", "needs_review", "failed",
            name="document_status",
            create_type=False
        ),
        nullable=False,
        server_default="queued"
    )
    failure_stage = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)
    doc_type = Column(Text, nullable=True)
    read_method = Column(Text, nullable=True)
    ocr_confidence = Column(Numeric(5, 2), nullable=True)
    raw_text = Column(Text, nullable=True)
    engine = Column(Text, nullable=True)
    ai_model = Column(Text, nullable=True)
    ai_input_tokens = Column(Integer, nullable=False, server_default="0")
    ai_output_tokens = Column(Integer, nullable=False, server_default="0")
    attempts = Column(Integer, nullable=False, server_default="0")
    processing_ms = Column(Integer, nullable=True)
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    batch = relationship("Batch", back_populates="documents")
    extracted_fields = relationship("ExtractedField", back_populates="document", uselist=False, cascade="all, delete-orphan")
    validation_flags = relationship("ValidationFlag", back_populates="document", cascade="all, delete-orphan")
    processing_events = relationship("ProcessingEvent", back_populates="document", cascade="all, delete-orphan", order_by="ProcessingEvent.created_at.asc()")
    field_edits = relationship("FieldEdit", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_documents_user_id_status", "user_id", "status"),
        Index("ix_documents_user_id_created_at_desc", "user_id", text("created_at DESC")),
        Index("ix_documents_sha256", "sha256"),
    )


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True)
    doc_no = Column(Text, nullable=True)
    doc_date = Column(Date, nullable=True)
    vendor_name = Column(Text, nullable=True)
    vendor_gstin = Column(Text, nullable=True)
    buyer_name = Column(Text, nullable=True)
    buyer_gstin = Column(Text, nullable=True)
    place_of_supply = Column(Text, nullable=True)
    subtotal = Column(Numeric(14, 2), nullable=True)
    cgst = Column(Numeric(14, 2), nullable=True)
    sgst = Column(Numeric(14, 2), nullable=True)
    igst = Column(Numeric(14, 2), nullable=True)
    round_off = Column(Numeric(14, 2), nullable=True)
    total = Column(Numeric(14, 2), nullable=True)
    currency = Column(CHAR(3), nullable=False, server_default="INR")
    financial_year = Column(Text, nullable=True)
    sources = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    ai_raw = Column(JSONB, nullable=True)
    rules_raw = Column(JSONB, nullable=True)
    ai_note = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    document = relationship("Document", back_populates="extracted_fields")

    __table_args__ = (
        Index("ix_extracted_fields_vendor_gstin_doc_no", "vendor_gstin", "doc_no"),
    )


class ValidationFlag(Base):
    __tablename__ = "validation_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    level = Column(
        Enum("error", "warning", "info", name="flag_level", create_type=False),
        nullable=False
    )
    code = Column(Text, nullable=False)
    field = Column(Text, nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document = relationship("Document", back_populates="validation_flags")


class ProcessingEvent(Base):
    __tablename__ = "processing_events"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    stage = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document = relationship("Document", back_populates="processing_events")


class FieldEdit(Base):
    __tablename__ = "field_edits"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field = Column(Text, nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    edited_by = Column(UUID(as_uuid=True), nullable=True)
    edited_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document = relationship("Document", back_populates="field_edits")


class WorkerHeartbeat(Base):
    __tablename__ = "worker_heartbeat"

    id = Column(Integer, primary_key=True, default=1, server_default="1")
    beat_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

