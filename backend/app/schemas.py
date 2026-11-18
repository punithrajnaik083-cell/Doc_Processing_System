from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class ValidationFlagSchema(BaseModel):
    id: Optional[UUID] = None
    level: str
    code: str
    field: Optional[str] = None
    message: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProcessingEventSchema(BaseModel):
    id: Optional[UUID] = None
    stage: str
    message: str
    duration_ms: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ExtractedFieldsSchema(BaseModel):
    doc_no: Optional[str] = None
    doc_date: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_gstin: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None
    place_of_supply: Optional[str] = None
    subtotal: Optional[str] = None
    cgst: Optional[str] = None
    sgst: Optional[str] = None
    igst: Optional[str] = None
    round_off: Optional[str] = None
    total: Optional[str] = None
    currency: str = "INR"
    financial_year: Optional[str] = None
    sources: dict[str, str] = Field(default_factory=dict)
    ai_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentSummary(BaseModel):
    id: UUID
    filename: str
    status: str
    doc_type: Optional[str] = None
    vendor_name: Optional[str] = None
    doc_no: Optional[str] = None
    doc_date: Optional[str] = None
    total: Optional[str] = None
    error_count: int = 0
    warning_count: int = 0
    created_at: datetime
    failure_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentDetail(BaseModel):
    id: UUID
    user_id: UUID
    batch_id: Optional[UUID] = None
    filename: str
    ext: str
    mime_type: str
    size_bytes: int
    sha256: str
    page_count: Optional[int] = None
    status: str
    failure_stage: Optional[str] = None
    failure_reason: Optional[str] = None
    doc_type: Optional[str] = None
    read_method: Optional[str] = None
    ocr_confidence: Optional[float] = None
    engine: Optional[str] = None
    ai_model: Optional[str] = None
    ai_input_tokens: int = 0
    ai_output_tokens: int = 0
    attempts: int = 0
    processing_ms: Optional[int] = None
    claimed_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    fields: Optional[ExtractedFieldsSchema] = None
    flags: list[ValidationFlagSchema] = Field(default_factory=list)
    events: list[ProcessingEventSchema] = Field(default_factory=list)
    preview_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

